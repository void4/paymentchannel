contract Channel {

    struct PaymentChannel {
        address sender;
        address receiver;
        uint256 value;
        uint256 validUntil;

        bool valid;
    }

    mapping(uint => PaymentChannel) public channels;
    uint id;

    event NewChannel(address indexed sender, address indexed receiver, uint channel);
    event Deposit(address indexed sender, address indexed receiver, uint channel);
    event Claim(address indexed who, uint indexed channel);
    event Reclaim(bytes32 indexed channel);

    function Channel() {
        id = 0;
    }

    function createChannel(address receiver, uint256 expiry) {
        uint channel = id++;
        channels[channel] = PaymentChannel(msg.sender, receiver, msg.value, expiry, true);

        NewChannel(msg.sender, receiver, channel);
    }

    // creates a hash using the recipient and value.
    function getHash(uint channel, address recipient, uint value) constant returns(bytes32) {
        return sha3(address(this), channel, recipient, value);
    }

    // verify a message (receipient || value) with the provided signature
    function verify(uint channel, address recipient, uint value, uint8 v, bytes32 r, bytes32 s) constant returns(bool) {
        PaymentChannel ch = channels[channel];
        return ch.valid && ch.validUntil > block.timestamp && ch.receiver == recipient && ch.sender == ecrecover(getHash(channel, recipient, value), v, r, s);
    }

    // claim funds
    function claim(uint channel, address recipient, uint value, uint8 v, bytes32 r, bytes32 s) {
        if( !verify(channel, recipient, value, v, r, s) ) return;

        PaymentChannel ch = channels[channel];
        if( value > ch.value ) {
            recipient.send(ch.value);
            ch.value = 0;
        } else {
            recipient.send(value);
            ch.value -= value;
        }

        // channel is no longer valid
        channels[channel].valid = false;

        Claim(recipient, channel);
    }

    function deposit(uint channel) {
        if( !isValidChannel(channel) ) throw;

        PaymentChannel ch = channels[channel]; 
        ch.value += msg.value;

        Deposit(msg.sender, ch.receiver, channel);
    }

    // reclaim a channel
    function reclaim(uint channel) {
        PaymentChannel ch = channels[channel];
        if( ch.value > 0 && ch.validUntil < block.timestamp ) {
            ch.sender.send(ch.value);
            delete channels[channel];
        }
    }

    function getChannelValue(uint channel) constant returns(uint256) {
        return channels[channel].value;
    }

    function getChannelSender(uint channel) constant returns(address) {
        return channels[channel].sender;
    }

    function getChannelReceiver(uint channel) constant returns(address) {
        return channels[channel].receiver;
    }

    function  getChannelValidUntil(uint channel) constant returns(uint) {
        return channels[channel].validUntil;
    }
    function isValidChannel(uint channel) constant returns(bool) {
        PaymentChannel ch = channels[channel];
        return ch.valid && ch.validUntil >= block.timestamp;
    }
}
