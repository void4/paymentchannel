contract Channel {

    struct PaymentChannel {
        address sender;
        address receiver;
        uint256 value;
        uint256 expiry;

        bool valid;
    }

    PaymentChannel[] public channels;

    event NewChannel(address indexed sender, address indexed receiver, uint channel);
    event Deposit(address indexed sender, address indexed receiver, uint channel);
    event Claim(address indexed who, uint indexed channel);
    event Reclaim(bytes32 indexed channel);

    function createChannel(address receiver, uint256 expiry) {
        channels.push(PaymentChannel(msg.sender, receiver, msg.value, expiry, true));
        NewChannel(msg.sender, receiver, channels.length);
    }

    // creates a hash using the recipient and value.
    function getHash(uint channel, uint value) constant returns(bytes32) {
        return sha3(address(this), channel, value);
    }

    // verify a message (receipient || value) with the provided signature
    function verify(uint channel, uint value, uint8 v, bytes32 r, bytes32 s) constant returns(bool) {
        PaymentChannel ch = channels[channel];
        return ch.valid && ch.expiry > block.timestamp && ch.sender == ecrecover(getHash(channel, value), v, r, s);
    }

    // claim funds
    function claim(uint channel, uint value, uint8 v, bytes32 r, bytes32 s) {
        if( !verify(channel, value, v, r, s) ) return;

        PaymentChannel ch = channels[channel];

        if (msg.sender != ch.receiver) throw;

        if( value > ch.value ) {
            ch.receiver.send(ch.value);
            ch.value = 0;
        } else {
            ch.receiver.send(value);
            ch.value -= value;
        }

        // channel is no longer valid
        channels[channel].valid = false;

        Claim(ch.receiver, channel);
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
        if( ch.value > 0 && ch.expiry < block.timestamp ) {
            ch.sender.send(ch.value);
            delete channels[channel];
        }
    }

    function isValidChannel(uint channel) constant returns(bool) {
        PaymentChannel ch = channels[channel];
        return ch.valid && ch.expiry >= block.timestamp;
    }
}
