# zkp-schnorr-demo
A Python implementation of the Schnorr Zero-Knowledge Proof (ZKP) protocol for secure password authentication without transmitting secrets.

## Overview

In traditional authentication, you send your password to the server. If the server is hacked, your password is stolen. 
In this **Zero-Knowledge Proof (ZKP)** system:
1. The Server **never** sees the password.
2. The Server **never** stores the password.
3. The Server stores only a cryptographic public key.
4. The Client proves they know the password using advanced mathematics.

## How to Run

### Option 1: Python Script
Run the interactive simulation directly in your terminal:
```bash
python3 zkp_auth.py
