from iota import *
import gnupg
import time

#Connects to node and opens API stream with seed
node = "http://iota.teamveno.eu:14265"
seed = "FZVHIPWMPGSEUTFZMEVSMPUXZWMKLNRAEMYKKUTU9DFQIK99UKYPAZVGVCNHRYHAIETUI"
api = Iota(node, seed)
#print(api.get_node_info())

#print(api.get_new_addresses(index=0, count=1)['addresses'])

gpg = gnupg.GPG(homedir="gpg")

def get_bundles(n=None):
	return api.get_transfers(start=n).get(u'bundles')

def print_messages(ms):  #Takes a list of bundles
	for m in ms:
		for tx in m:
			print(TryteString.decode(tx.signature_message_fragment))

def interpret_message(m):  #Executes appropriate command based on message received
	tx = m[0]
	raw = TryteString.decode(tx.signature_message_fragment)
	msg = str(gpg.decrypt(raw, passphrase="iotrocks"))

	msg = msg.split(",")

	time_difference = int(time.time()) - int(msg[0])

	if time_difference <= 120 and not(time_difference < 0):
		if msg[1]=="open":
			print("Received opening instruction. Opening lock.")

			verify = gpg.verify(raw).valid
			print("signature validity:")
			print(verify)
		else:
			print("Unrecognized instruction.")
	else:
		print("Timestamp is too far off ("+str(time_difference)+").")


def listen_loop():  #Checks transactions for new lock/unlock commands
    ms = get_bundles()
    n = len(ms)
    print("Found", n, "old message(s):")
    #print_messages(ms)
    print("------------------------")

    print("Waiting for new messages:")
    while(True):
        ms = get_bundles()  #TODO This is a bottleneck
        if len(ms)==n:
            print("No new messages")
        else:
            print("Received", len(ms)-n, "new message(s) [decrypted]:")
            interpret_message(ms[-1])
            n = len(ms)

listen_loop()
