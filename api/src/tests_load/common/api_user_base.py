from locust import HttpUser, events
import yaml

from common.util import authenticate

@events.init_command_line_parser.add_listener
def setup_command_line_parser(parser):
    parser.add_argument(
        '--test_fixtures',
        type=str,
        help='Path to a json independent of Locust that configures the tests with things like credentials',
        required=True
    )

class APIUserBase(HttpUser):
    abstract = True

    def on_start(self):
        with open(self.environment.parsed_options.test_fixtures, 'r') as f:
            self._config = yaml.safe_load(f)

        jwt = authenticate(
            self.environment.parsed_options.host,
            '/auth/token',
            self._config['username'],
            self._config['password']
        )
        self.client.headers = {
            'Authentication': f"Bearer {jwt}"
        }
        
        # ! Might break on a different version of Locust
        #   Only Basic authentication supported by Locust natively.
        #   This isn't documented, but it's how the FastHttpSession saves credentials internally
        # Workaround for authentication needing to happen after we have an instance of FastHttpUser (so we have self.environment.parsed_options), 
        # And also before building a FastHttpUser instance since it builds its client (passing default_headers to it) in the constructor  
        self.client.headers = {
            'Authorization': f"Bearer {jwt}"
        } 

        return super().on_start()
