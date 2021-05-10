#!/usr/bin/env python3

import asyncio, requests, sys, os, dns.resolver, json
from discord import Webhook, RequestsWebhookAdapter
from urllib.parse import urlparse
from dns.resolver import Resolver, NXDOMAIN, NoNameservers, Timeout, NoAnswer
from pathlib import Path

home = str(Path.home())

class takeover:
    def __init__(self, configuration):
        self.inform = Webhook.from_url(configuration['discord_webhook'], adapter=RequestsWebhookAdapter())
        self.fingerprints = configuration['fingerprints']
        self.discord_user_id = configuration['user_id'] if('user_id' in configuration) else ""

    async def subDomainTakeOver(self, domain, cname, fingerprint):
        for rdata in cname:
            for cname in fingerprint['cname']:
                if(cname and cname in str(rdata.target)):
                    website = 'http://' + domain
                    request = requests.get(website)
                    if(fingerprint['fingerprint'] in request.text):
                        print("[+] %s matched for domain %s" % (fingerprint['service'], domain))
                        self.inform.send("""
                            Hey%s,\n%s is %s to subdomain takeover on %s. Fingerprint is `%s`
                        """ % (('<@' + self.discord_user_id + '>') if self.discord_user_id else "", website, fingerprint['status'].lower().strip(), fingerprint['service'], fingerprint['fingerprint']))
  
    async def checkHosts(self, args=[]):
        recheck = []
        try:
            if(not len(args)):
                args = sys.argv
                args.pop(0)
            if(not len(args)):
                print("Reading from PIPE... Raise KeyboardInterrupt to stop it.")
                args = list(set(sys.stdin))

            for domain in args:
                validdomain = domain
                if not(domain.startswith('http://') or domain.startswith('https://')):
                    validdomain = (urlparse('http://' + domain).netloc).strip()
                try:
                    cname = dns.resolver.query(validdomain, 'CNAME')
                    [await self.subDomainTakeOver(validdomain, cname, fingerprint) for fingerprint in self.fingerprints]

                except NoNameservers:
                    print("[x] DNS No No nameservers: %s" % validdomain)
                except Timeout:
                    recheck.append(validdomain)
                    print("[x] DNS Timeout: %s"  % validdomain)
                except NoAnswer:
                    print("[x] DNS No Answer for CNAME: %s"  % validdomain)
                except NXDOMAIN:
                    print("[x] DNS NXDOMAIN: %s"  % validdomain)

            if(len(recheck)):
                await self.checkHosts(recheck)

        except IndexError:
            print("[x] No argument provided!")
            exit(1)
        except KeyboardInterrupt:
            print("[x] KeyboardInterrupt occurred.")
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