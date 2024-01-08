from locust import FastHttpUser, events
import yaml

from common.util import authenticate


@events.init_command_line_parser.add_listener
def setup_command_line_parser(parser):
    parser.add_argument(
        "--test_config",
        type=str,
        help="Path to a yaml file independent of Locust that configures the tests with things like credentials",
        required=False,
    )


class APIUserBase(FastHttpUser):
    abstract = True
    test_config = {}

    def on_start(self):
        self.test_config = APIUserBase.test_config

        # to opt out from authenticating / adding the auth header (as an external client would) or guarantee that the test is always readonly,
        #   just don't specify username/password in the test class
        if self.test_config.get("username", None) and self.test_config.get(
            "password", None
        ):
            jwt = authenticate(
                self.environment.parsed_options.host,
                "/auth/token",
                self.test_config["username"],
                self.test_config["password"],
            )

            # ! Might break on a different version of Locust
            #   Only Basic authentication supported by Locust natively.
            #   This isn't documented, but it's how the FastHttpSession saves credentials internally
            # Workaround for authentication needing to happen after we have an instance of FastHttpUser (so we have self.environment.parsed_options),
            # And also before building a FastHttpUser instance since it builds its client (passing default_headers to it) in the constructor
            self.client.auth_header = f"Bearer {jwt}"

        return super().on_start()


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    if getattr(environment.parsed_options, "test_config"):
        with open(environment.parsed_options.test_config, "r") as f:
            APIUserBase.test_config = yaml.safe_load(f)
