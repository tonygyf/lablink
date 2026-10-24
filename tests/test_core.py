import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lablink import config, transport
from lablink.addons import server_script


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lablink test ")
        self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, {"LABLINK_HOME": self.tmp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.c = dict(config.DEFAULT, host="server.example.org", user="researcher")

    def test_non_object_config_is_rejected(self):
        for value in ([], None, 1, "invalid"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                config.validate(value)

    def test_blank_template_requires_input(self):
        with self.assertRaises(ValueError):
            config.validate(config.DEFAULT)

    def test_injection_hosts_rejected(self):
        for host in ["-oProxyCommand=evil", "name;touch /tmp/x", "name\nother", "user@host", "$(id)"]:
            with self.subTest(host=host), self.assertRaises(ValueError):
                config.validate(dict(self.c, host=host))

    def test_ipv6_is_supported(self):
        config.validate(dict(self.c, host="2001:db8::1"))

    def test_bad_ports(self):
        for port in [-1, 65536, "22", True]:
            with self.subTest(port=port), self.assertRaises(ValueError):
                config.validate(dict(self.c, ssh_port=port))

    def test_panel_cannot_redirect_to_another_host(self):
        for path in ["//evil.test", "https://evil.test", "/\\evil.test", "/x\n"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                config.validate(dict(self.c, panel_path=path))

    def test_config_roundtrip_and_permissions(self):
        config.save(self.c)
        self.assertEqual(config.load(), self.c)
        self.assertFalse((config.home() / "config.tmp").exists())
        if os.name != "nt":
            self.assertEqual((config.home() / "config.json").stat().st_mode & 0o777, 0o600)

    def test_invalid_save_does_not_replace_valid_config(self):
        config.save(self.c)
        with self.assertRaises(ValueError):
            config.save(dict(self.c, user="bad user"))
        self.assertEqual(config.load(), self.c)

    def test_unknown_fields_reject_secret_storage(self):
        with self.assertRaises(ValueError):
            config.validate(dict(self.c, password="secret"))

    def test_ssh_has_isolated_config_and_host_key_checking(self):
        with patch.object(transport, "executable", return_value="/trusted/ssh"):
            args = transport.ssh_args(self.c)
        self.assertEqual(args[0], "/trusted/ssh")
        self.assertIn(os.devnull, args)
        self.assertIn("StrictHostKeyChecking=ask", args)
        self.assertIn(f"UserKnownHostsFile={config.home() / 'known_hosts'}", args)

    def test_key_with_spaces_is_one_argument(self):
        key = Path(self.tmp.name) / "key with spaces"
        key.write_text("test fixture, not an actual key")
        with patch.object(transport, "executable", return_value="/trusted/ssh"):
            args = transport.ssh_args(dict(self.c, identity_file=str(key)))
        self.assertEqual(args[args.index("-i") + 1], str(key.resolve()))

    def test_tunnel_starts_on_loopback_and_cleans_up_on_exception(self):
        # Actual child process, but no SSH server or user credentials involved.
        stub = Path(self.tmp.name) / "fake_ssh.py"
        stub.write_text('''import socket,sys,time
spec=sys.argv[sys.argv.index('-L')+1].split(':')
s=socket.socket();s.bind((spec[0],int(spec[1])));s.listen()
while True:
 c,a=s.accept();c.close()
''')
        children = []
        original = subprocess.Popen
        def spawn(*a, **k):
            p = original(*a, **k)
            children.append(p)
            return p
        with patch.object(transport, "ssh_args", return_value=[sys.executable, str(stub)]), patch.object(transport.subprocess, "Popen", side_effect=spawn):
            with self.assertRaisesRegex(RuntimeError, "test cleanup"):
                with transport.tunnel(self.c, 5900, timeout=5) as port:
                    with socket.create_connection(("127.0.0.1", port), timeout=1):
                        pass
                    raise RuntimeError("test cleanup")
        self.assertIsNotNone(children[0].poll())

    def test_tunnel_failure_is_not_reported_as_ready(self):
        with patch.object(transport, "ssh_args", return_value=[sys.executable, "-c", "raise SystemExit(1)"]):
            with self.assertRaises(ValueError):
                with transport.tunnel(self.c, 5900, timeout=2):
                    self.fail("failed process yielded a tunnel")

    def test_installers_are_official_and_do_not_disable_host_security(self):
        self.assertIn("https://tailscale.com/install.sh", server_script("tailscale"))
        self.assertIn("https://resource.fit2cloud.com/", server_script("1panel"))
        self.assertNotIn("ufw disable", server_script("vnc"))


if __name__ == "__main__":
    unittest.main()
