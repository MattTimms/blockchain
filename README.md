# blockchain
An implementation of the blockchain. Educational purposes mostly.

>> I still don't get bitcoin  

>> Image if keeping your car idling 24/7 produced solved Sudokus you could trade for heroin   


### brief description
``` 
A blockchain is an immutable, sequential chain of records called Blocks.
They contain any data, but more importantly they are chained together using hashes.
If a hash is corrupted by an attacker than all subsequent blocks will have incorrect hashes.

To create/mine new Blocks, the Proof of Work algorithm must be solved. This algorithm discovers a number 
which solves a problem; it must be difficult to solve but easy to verify computationally.

To ensure consensus amongst nodes, we make the rule that the longest valid chain is authoritative.
```



### slightly longer description
* I have a series of transaction data: sender, recipient, & the amount transferred. These transaction entries are stored
in a _Block_. A SHA-256 hash is created from this serialised block; thus, any changes to the Block will change the 
Block's hash. This prevents modifications to Blocks because it will invalidate the hash.

* What determines Block validity?  
The proof-of-work algorithm intends to be hard to solve but easy to verify; e.g. Sudoku.   
In this example, the task is to find the proof string _p_ such that the hash of the concatenation of ( _p'_ _p_ ), 
where _p'_ is the previous Block's proof, provides a hash with four leading zeros.   
Computational difficulty can scale with the number of leading zeros required. 

* How do all the interconnected parts work?  
A node has a record of the Blockchain from consensus with other nodes. Transactions are sent to the node and stored for the node's next Block. 
Once the node solves the proof-of-work algorithm, it may attach a transaction of "new unit of currency" to it's 
transaction ID. It then hashes it's contents and appends to the Blockchain.

N.B. Crypto's act differently; transactions require consensus, the blockchain updates every ten minutes, etc.


### usage
Either `python3 app.py` or `make docker`.  
Then use _PostMan_ or equivalent to make HTTP requests. See `app.py` for API.

### references
 - https://hackernoon.com/learn-blockchains-by-building-one-117428612f46