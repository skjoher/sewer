import urllib.parse

import requests

from dns.resolver import Resolver

from . import common
from ..lib import log_response


class AcmeDnsDns(common.BaseDns):
    def __init__(self, ACME_DNS_API_USER, ACME_DNS_API_KEY, ACME_DNS_API_BASE_URL, **kwargs):
        self.ACME_DNS_API_USER = ACME_DNS_API_USER
        self.ACME_DNS_API_KEY = ACME_DNS_API_KEY
        self.HTTP_TIMEOUT = 65  # seconds

        if ACME_DNS_API_BASE_URL[-1] != "/":
            self.ACME_DNS_API_BASE_URL = ACME_DNS_API_BASE_URL + "/"
        else:
            self.ACME_DNS_API_BASE_URL = ACME_DNS_API_BASE_URL
        super().__init__(**kwargs)

    def create_dns_record(self, domain_name, domain_dns_value):
        self.logger.info("create_dns_record")

        resolver = Resolver(configure=False)
        resolver.nameservers = ["172.31.31.31"]
        answer = resolver.query("_acme-challenge.{0}.".format(domain_name), "TXT")
        subdomain, _ = str(answer.canonical_name).split(".", 1)

        url = urllib.parse.urljoin(self.ACME_DNS_API_BASE_URL, "update")
        headers = {"X-Api-User": self.ACME_DNS_API_USER, "X-Api-Key": self.ACME_DNS_API_KEY}
        body = {"subdomain": subdomain, "txt": domain_dns_value}
        update_acmedns_dns_record_response = requests.post(
            url, headers=headers, json=body, timeout=self.HTTP_TIMEOUT
        )
        self.logger.debug(
            "update_acmedns_dns_record_response. status_code={0}. response={1}".format(
                update_acmedns_dns_record_response.status_code,
                log_response(update_acmedns_dns_record_response),
            )
        )
        if update_acmedns_dns_record_response.status_code != 200:
            # raise error so that we do not continue to make calls to ACME
            # server
            raise ValueError(
                "Error creating acme-dns dns record: status_code={status_code} response={response}".format(
                    status_code=update_acmedns_dns_record_response.status_code,
                    response=log_response(update_acmedns_dns_record_response),
                )
            )
        self.logger.info("create_dns_record_end")

    def delete_dns_record(self, domain_name, domain_dns_value):
        self.logger.info("delete_dns_record")
        # acme-dns doesn't support this
        self.logger.info("delete_dns_record_success")
