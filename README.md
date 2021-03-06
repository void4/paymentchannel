## Ethereum payment channels for Python

![Example](example.png)

This is an improved implementation of the https://github.com/obscuren/whisper-payment-channel contract.

Changelog:
- renamed owner and beneficiary to sender and receiver, validUntil to expiry
- to avoid sender using one channel for different receivers, added an address field to the payment channel data structure
- included the channel contracts address in getHash, to prevent reuse of signatures in a new contract instance
- only allow receiver to claim channel, to prevent attacks resulting in costs for opening and closing new channels

#### Open questions
###### Should the contract use the receiver address or channel id as event index? (except for NewChannel)
###### Is there a reason to use hash as channel id instead of incrementing integer?
