import random
import hashlib
import sys

# --- GLOBAL PARAMETERS ---
# In a real-world scenario (like Bitcoin), P would be a 256-bit prime number (secp256k1).
# We use a smaller prime here so the math is easy to inspect and debug.
# P: A large prime number
# G: A generator element of the finite field
P = 48611
G = 19

def hash_password_to_int(password_str):
    """
    Converts a text string (e.g., "secret123") into a mathematical integer 'x'.
    1. SHA256 hashes the string to get a unique hex digest.
    2. Converts hex to a large integer.
    3. Modulo (P-1) ensures the exponent fits within our finite field.
    """
    sha_signature = hashlib.sha256(password_str.encode()).hexdigest()
    big_int = int(sha_signature, 16)
    secret_int = big_int % (P - 1)
    return secret_int

class Prover:
    """
    The Legitimate User (Peggy).
    Knows the secret password 'x'.
    """
    def __init__(self, password_str):
        self.secret_x = hash_password_to_int(password_str)
        self.r = 0 # Ephemeral random nonce

    def register(self):
        """
        Calculates the public key 'y' to share with the server.
        y = g^x mod p
        """
        public_y = pow(G, self.secret_x, P)
        return public_y

    def generate_commitment(self):
        """
        Step 1: Generate a random number 'r' and a commitment 't'.
        t = g^r mod p
        """
        self.r = random.randint(1, P - 2)
        t = pow(G, self.r, P)
        return t

    def solve_challenge(self, c):
        """
        Step 3: Calculate the proof response 's'.
        s = r + c * x
        """
        s = self.r + (c * self.secret_x)
        return s

class FakeProver:
    """
    The Attacker (Mallory).
    Does NOT know the password, but attempts to spoof the protocol.
    """
    def __init__(self):
        self.r = 0

    def generate_commitment(self):
        # Mallory can generate a valid 't' because she can pick a random 'r'
        self.r = random.randint(1, P - 2)
        t = pow(G, self.r, P)
        return t

    def solve_challenge(self, c):
        # Mallory FAILS here. She needs 'x' to compute 's = r + c*x'.
        # Since she doesn't have it, she guesses '12345'.
        fake_x = 12345 
        s = self.r + (c * fake_x)
        return s

class Verifier:
    """
    The Server (Victor).
    Does NOT know the secret 'x'. Only stores the public key 'y'.
    """
    def __init__(self, public_key):
        self.public_y = public_key
        self.c = 0

    def generate_challenge(self):
        """
        Step 2: Generate a random challenge 'c'.
        """
        self.c = random.randint(1, 100)
        return self.c

    def verify(self, t, s):
        """
        Step 4: Verification.
        Checks if g^s == t * y^c (mod p)
        """
        # LHS: g^s mod p
        lhs = pow(G, s, P)
        
        # RHS: t * y^c mod p
        rhs = (t * pow(self.public_y, self.c, P)) % P
        
        return lhs == rhs

# --- MAIN SIMULATION LOOP ---
def run_simulation():
    print("--- ZKP AUTHENTICATION SYSTEM (SCHNORR) ---")
    
    # 1. Registration Phase
    raw_pass = input("Enter a password to register: ")
    real_peggy = Prover(raw_pass)
    public_key = real_peggy.register()
    
    print(f"\n[Database] Stored Public Key (y): {public_key}")
    print(f"[Database] Server does NOT know the password.")
    print("-" * 50)

    # Instantiate Server with the public key
    server = Verifier(public_key)

    while True:
        print("\nSELECT ACTION:")
        print("1. Login as Legitimate User")
        print("2. Attempt Hack (Man-in-the-Middle)")
        print("3. Exit")
        choice = input("Option: ")

        if choice == '1':
            print("\n--- AUTHENTICATING USER ---")
            # Step 1: Commitment
            t = real_peggy.generate_commitment()
            print(f"-> Client sends Commitment (t): {t}")

            # Step 2: Challenge
            c = server.generate_challenge()
            print(f"<- Server sends Challenge (c): {c}")

            # Step 3: Response
            s = real_peggy.solve_challenge(c)
            print(f"-> Client sends Response (s): {s}")

            # Step 4: Verification
            if server.verify(t, s):
                print(">> ACCESS GRANTED: Mathematical proof valid.")
            else:
                print(">> ACCESS DENIED: Proof invalid.")

        elif choice == '2':
            print("\n--- ATTACK SIMULATION START ---")
            print("Hacker trying to login using the User's public key...")
            
            fake_peggy = FakeProver()
            
            # Step 1: Commitment 
            t = fake_peggy.generate_commitment()
            print(f"-> Hacker sends valid Commitment (t): {t}")

            # Step 2: Challenge
            c = server.generate_challenge()
            print(f"<- Server sends Challenge (c): {c}")

            # Step 3: Response (Hacker fails here)
            s = fake_peggy.solve_challenge(c)
            print(f"-> Hacker sends Fake Response (s): {s}")

            # Step 4: Verification
            if server.verify(t, s):
                print(">> FATAL ERROR: Hacker bypassed security!")
            else:
                print(">> ACCESS DENIED: The math didn't add up. Hacker caught.")

        elif choice == '3':
            print("Exiting.")
            break

if __name__ == "__main__":
    run_simulation()
