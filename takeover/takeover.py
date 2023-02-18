import click, requests, dns.resolver, json, time, sys, os
from concurrent import futures
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class UnknownService(Exception):
    def __init__(self, message="Service is invalid. Make sure the service is compliant with https://github.com/EdOverflow/can-i-take-over-xyz."):
        super().__init__(self.message)

class Config:
    def __init__(self, configFile="./config.json"):
        try:
            if(configFile.startswith("http://") or configFile.startswith("https://")):
                self.config = json.loads(requests.get(configFile).text)
            else:
                with open(configFile, 'r') as f:
                    self.config = json.load(f)
        except Exception as e:
            print("Failed to load config file! Exitting...", file=sys.stderr)
            print(e, file=sys.stderr)
            exit(1)

    def services(self):
        return self.config["fingerprints"]
    
    def channel(self, name):
        if(name == ""):
            return False
        for channel in self.config["config"]["channels"]:
            if channel["name"] == name:
                return channel

class Notifier:
    def __init__(self, channel):
        self.channel = channel
    
    def send(self, target, service):
        self.headers = self.channel["headers"]
        for header in self.headers.keys():
            self.headers[header] = self.headers[header].format(GITHUB_TOKEN="GITHUB_TOKEN")
        
        self.webhook = self.channel["webhook"].format(
            WEBHOOK_URL=os.getenv("WEBHOOK_URL"),
            TELEGRAM_BOT_TOKEN=os.getenv("BOT_TOKEN"),
            GITHUB_USER=os.getenv("GITHUB_USER"),
            GITHUB_REPOSITORY=os.getenv("GITHUB_REPOSITORY")
        )
        
        message = ("{" + self.channel["body"] + "}").format(
            TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID"),
            MESSAGE=self.channel["message_template"].format(
                TARGET=target.target,
                STATUS=service["status"],
                SERVICE=service["service"],
                DOCUMENTATION=service["documentation"]
            )
        )

        try:
            print(requests.post(self.webhook, data=message, headers=self.headers).text)
            print("Notified %s" % self.channel["name"], file=sys.stderr)
        except Exception as e:
            print("Failed to notify %s" % self.channel["name"], file=sys.stderr)
            print(e)

class Target:
    def __init__(self, domain, driver = "requests", browser = None):
        self.target = domain
        self.cnames = None
        self.html = None
        self.driver = driver
        self.browser = webdrivers[driver]["driver"]() if browser == None else browser
        self.driver = "chrome" if driver == None else driver      
    
    def check(self, service):
        try:
            if(service["status"] in ["Vulnerable", "Edge case"]):
                if(service["nxdomain"]):
                    self.resolved = dns.resolver.resolve(self.target) if self.cnames == None else self.cnames                  
                    for resolved_host in self.resolved:
                        if(str(resolved_host) in service["cname"]):
                            return service["status"]
                else:
                    if self.html == None:
                        response = self.browser.get("http://" + self.target)
                        time.sleep(2)
                        self.html = getattr(response, webdrivers[self.driver]["content_attribute"])

                    if(service["fingerprint"] in self.html):
                        return service["status"]
        except KeyError:
            raise UnknownService

        return "Not vulnerable"
        

webdrivers = {
    "chrome": {
        "driver": webdriver.Chrome,
        "content_attribute": "page_source",
    },
    "firefox": {
        "driver": webdriver.Firefox,
        "content_attribute": "page_source",
    },
    "requests": {
        "driver": lambda: requests,
        "content_attribute": "text",
    }
}

def check(domain, services, channel):
    try:
        target = Target(domain)
        result = False

        for service in services:
            result = target.check(service)
            print("[%s] %s: %s" % (domain, service["service"].strip(), result), file=sys.stderr)
            
            if(channel):
                if result in channel["report"]:
                    notify = Notifier(channel)
                    notify.send(target, service)
        
    except Exception as e:
        print("%s" % e.__repr__(), file=sys.stderr)

# Commands
@click.command()
@click.argument('subdomains', type=click.File('r'))
@click.option('--max-threads', default=10, help='Maximum number of threads to use.')
@click.option('--config', default="", help='Location of config file. Can also be a URL')
@click.option('--services', default="", help='Location of fingerprints file. Can also be a URL. If blank, fingerprints from config file will be used.')
@click.option('--driver', default="requests", type=click.Choice(['chrome', 'firefox', 'requests']), help='Driver to use to fetch html content. Default: requests.')
@click.option('--notify', default="", type=click.Choice(['', 'Discord', 'Telegram', 'Slack', 'GitHub Issue']), help='Location of config file. Can also be a URL')
def main(subdomains, max_threads, config, services, driver, notify):
    """
    This command accepts a list of domain names and checks for possible takeovers.

    :param subdomains: A file-like object containing a list of domain names, one per line.
    :param max_threads: The maximum number of threads to use for checking the domains.
    """
    config = Config() if config == "" else config
    services = json.loads(requests.get(services).text) if services != "" else config.services()
    
    print("Found fingerprints: %s" % len(services), file=sys.stderr)
    
    try:
        driver = webdrivers[driver]["driver"]()
    except (KeyError, WebDriverException) as e:
        print("Browser not found, defaulting to requests module...", file=sys.stderr)
        print(e, file=sys.stderr)
        driver = webdrivers["requests"]["driver"]()
    
    max_threads = max_threads if max_threads > 0 else 1
    jobs = []
    with futures.ThreadPoolExecutor(max_workers=max_threads) as e:
        e.map(lambda domain: check(domain.strip(), services, config.channel(notify)), subdomains)
