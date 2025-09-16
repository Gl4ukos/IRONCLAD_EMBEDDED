Rpi is connected to "forth public access".
This network blocks all git push/pull requests from port 22 (the default port)

To use github effectively do:

-> Generate ssh key
-> Add ssh public key to github & private key to agent <ssh-add ~/.ssh/id_rsa>


-> Suppose new port: 443
-> Check connection from new port, type in terminal:  
ssh -T -p 443 git@ssh.github.com

-> Chenge the remote repo to (type in terminal):
 remote set-url origin ssh://git@ssh.github.com:443/Gl4ukos/IRONCLAD_EMBEDDED.git


