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
        self.fingerprints = configuration['fingerprints']
        self.discord_user_id = configuration['user_id'] if('user_id' in configuration) else ""
        self.totalthreads = 0
        self.allthreads = []
        self.messages = []

    def subDomainTakeOver(self, domain, cnames, fingerprint):
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
                        self.messages.append("""
                            Hey%s,\n%s is %s to subdomain takeover on %s. Fingerprint is `%s`
                        """ % (('<@' + self.discord_user_id + '>') if self.discord_user_id else "", website, fingerprint['status'].lower().strip(), fingerprint['service'], fingerprint['fingerprint']))
        self.totalthreads -= 1

    def inform(self):
        if(self.discord):
            while True:
                try:
                    message = self.messages.pop()
                    self.discord.send(message)
                except:
                    continue


    async def checkHosts(self, args=[]):
        self.recheck = []
        notificationThread = threading.Thread(target=self.inform)
        notificationThread.start()

        try:
            if(not len(args)):
                args = sys.argv
                args.pop(0)
            if(not len(args)):
                print("Reading from PIPE... Raise KeyboardInterrupt to stop it.")
                args = list(set(sys.stdin))

            for domain in args:
                while self.totalthreads > 80:
                    print("[!] Threads exceeding: %s Threads" % self.totalthreads)
                    time.sleep(1)

                validdomain = domain
                if not(domain.startswith('http://') or domain.startswith('https://')):
                    validdomain = (urlparse('http://' + domain).netloc).strip()
                try:
                    cname = dns.resolver.query(validdomain, 'CNAME')
                    threads = [threading.Thread(target=self.subDomainTakeOver, args=(validdomain, cname, fingerprint)) for fingerprint in self.fingerprints]
                    [thread.start() for thread in threads]
                    self.allthreads.append(threads)
                    self.totalthreads += len(threads)

                except NoNameservers:
                    print("[x] DNS No No nameservers: %s" % validdomain)
                except Timeout:
                    recheck.append(validdomain)
                    print("[x] DNS Timeout: %s"  % validdomain)
                except NoAnswer:
                    print("[x] DNS No Answer for CNAME: %s"  % validdomain)
                except NXDOMAIN:
                    print("[x] DNS NXDOMAIN: %s"  % validdomain)

            [thread.join() for thread in totalthreads]

            if(len(self.recheck)):
                await self.checkHosts(self.recheck)

        except IndexError:
            print("[x] No argument provided!")
            exit(1)
        except KeyboardInterrupt:
            print("[x] KeyboardInterrupt occurred.")
            [thread.join() for thread in totalthreads]
            notificationThread.join()
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