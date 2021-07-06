#!/usr/bin/env python3

import asyncio, requests, sys, os, dns.resolver, json, threading, time
from discord import Webhook, RequestsWebhookAdapter
from urllib.parse import urlparse
from dns.resolver import Resolver, NXDOMAIN, NoNameservers, Timeout, NoAnswer
from pathlib import Path

home = str(Path.home())

class takeover:
    def __init__(self, configuration):
        self.discord = Webhook.from_url(configuration['discord_webhook'], adapter=RequestsWebhookAdapter()) if configuration['discord_webhook'] else False
        self.discord_user_id = configuration['user_id'] if('user_id' in configuration) else ""
        
        self.fingerprints = configuration['fingerprints']
        self.totalthreads = 0
        self.allthreads = self.recheck = []
        self.messages = []
        self.found = set()

    def subDomainTakeOver(self, domain, cnames, fingerprint):
        key = "|".join([domain, fingerprint['service']])
        if key in self.found:
            return

        for rdata in cnames:
            for cname in fingerprint['cname']:
                if(cname and cname in str(rdata.target)):
                    website = 'http://' + domain
                    print("[.] Sending HTTP Request: %s" % domain)
                    try:
                        request = requests.get(website)
                    except requests.exceptions.ConnectionError:
                        print("[x] Connection Failed: %s" % domain)
                        self.recheck.append(domain)
                        return 
                    if(fingerprint['fingerprint'] in request.text):
                        print("[+] %s matched for domain %s" % (fingerprint['service'], domain))
                        self.found.add(key)
                        self.messages.append([website, fingerprint['status'].lower().strip(), fingerprint['service'], fingerprint['fingerprint']])
        self.totalthreads -= 1

        
    def inform(self):
        if(self.discord and len(self.messages)):
            message = "Hey %s, Subdomain takeovers here:\n```%s```" % (
                ('<@' + self.discord_user_id + '>') if self.discord_user_id else "",
                "\n".join([": ".join(message) for message in self.messages])
            )
            self.messages = []
            self.discord.send(message)


    async def checkHosts(self, args=[]):       
        args = (sys.argv[1:] if (not args) else args)
        if (not args):
            print("Reading from PIPE... Raise KeyboardInterrupt to stop it.")
            args = sys.stdin

        if (type(args) != enumerate):
            args = enumerate(args)

        try:
            for (index, domain) in args:
                while self.totalthreads > 80:
                    print("[!] Threads exceeding: %s Threads" % self.totalthreads)
                    time.sleep(1)

                if (domain.startswith('http://') or domain.startswith('https://')):
                    validdomain = (urlparse(domain).netloc).strip()
                else:
                    validdomain = (urlparse('http://' + domain).netloc).strip()

                try:
                    cname = dns.resolver.query(validdomain, 'CNAME')
                    threads = [threading.Thread(target=self.subDomainTakeOver, args=(validdomain, cname, fingerprint)) for fingerprint in self.fingerprints]
                    [thread.start() for thread in threads]
                    self.allthreads + threads
                    self.totalthreads += len(threads)

                except NoNameservers:
                    print("[x] DNS No No nameservers: %s" % validdomain)
                except Timeout:
                    self.recheck.append(validdomain)
                    print("[x] DNS Timeout: %s"  % validdomain)
                except NoAnswer:
                    print("[x] DNS No Answer for CNAME: %s"  % validdomain)
                except NXDOMAIN:
                    print("[x] DNS NXDOMAIN: %s"  % validdomain)

                self.inform()

            # [thread.join() for thread in self.allthreads]

        except IndexError:
            print("[x] No argument provided!")
            exit(1)
        except KeyboardInterrupt:
            print("[x] KeyboardInterrupt occurred.")
            [thread.join() for thread in self.allthreads]
            exit(1)


def main():
    try:
        config = json.load(open(home + "/.config/takeover/config.json"))
        config['fingerprints'] = json.load(open(home + "/.config/takeover/fingerprints.json"))
        config['user_id'] = config['user_id'] if 'user_id' in config else ""
    except FileNotFoundError:
        if('yes' == input("Takeover is not configured! To continue, you need to configure it. (type yes to continue): ")):
            config = {
                "fingerprints": input("Enter Path/URL for fingerprints.json. Leave blank to use default: ") or "https://gist.githubusercontent.com/0xcrypto/c0344960476193d8af7dbb310cc04958/raw/06ed5533702fc56b2e126eb600f8f8ce2967961d/sdto.json",
                "discord_webhook": input("Enter Discord webhook. Leave blank if you do not wish to use discord: "),
                "user_id": input("Enter your Discord User ID to get mentioned in the notification. Leave blank for no mention: ")
            }
            print("Your configuration is: ")
            print(json.dumps(config, sort_keys=True, indent=4))

            if(config['fingerprints'].startswith('http://') or config['fingerprints'].startswith('https://')):
                fingerprints = json.loads(requests.get(config['fingerprints']).text)
            else:
                fingerprints = json.load(open(config['fingerprints']))

            if('yes' == input("Would you like to save this? (yes to save the configuration, leave blank to use it temporarily): ")):
                if not os.path.exists(home + '/.config/takeover'):
                    os.makedirs(home + "/.config/takeover")
               
                with open(home + "/.config/takeover/fingerprints.json", 'w') as fingerprintFile:
                    json.dump(fingerprints, fingerprintFile)

                with open(home + "/.config/takeover/config.json", 'w') as configFile:
                    json.dump(config, configFile)

                print("Configuration file updated successfully!")

            config = {
                "discord_webhook": config['discord_webhook'],
                "fingerprints": fingerprints,
                "user_id": config['user_id'],
            }
        else:
            print("Without fingerprints, takeover cannot detect subdomain takeovers!")
            exit(1)

    asyncio.run(takeover(config).checkHosts())

if __name__ == '__main__':
    main()