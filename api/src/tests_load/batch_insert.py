from locust import task, HttpUser, events
import yaml

from common.util import authenticate, batch_response_status_all, make_image_payload

@events.init_command_line_parser.add_listener
def setup_command_line_parser(parser):
    parser.add_argument(
        '--test_fixtures',
        type=str,
        help='Path to a json independent of Locust that configures the tests with things like credentials',
        required=True
    )

class APIUser(HttpUser):
    _config = {
        # keep this up to date as a template, even though it's overwritten
        'study_uuid': None,
        'n_img_count': None,
        'username': None,
        'password': None
    }

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

    @task
    def batch_create_image(self):
        payload = make_image_payload(self._config['study_uuid'], self._config['n_img_count'])

        # , headers=self.default_headers
        rsp = self.client.post("api/private/images", json=payload)

        rsp_json = rsp.json()
        if not batch_response_status_all(rsp_json['items'], 201):
            rsp.failure("Unexpected status code")
        if rsp.elapsed.total_seconds() > 1:
            rsp.failure("Took too long")