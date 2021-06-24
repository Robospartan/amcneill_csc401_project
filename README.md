# amcneill_csc401_project
Networking project for setting up a P2P RFC sharing network with a central index.
Run the server.py python script with a command line argument for the hostname of the server.
ex: python server.py '127.0.0.1'
Run the peer.py python script with command line arguments for the hostname of the central server, for the hostname of the client for uploading RFCs, and for the RFC directory.
ex: python peer.py '127.0.0.1' '127.0.0.2' './rfc_dir'

Run commands on the peers as specified. The RFC Directory should contain only the RFCs, named in the format 'RFC RFC_Number Title'.