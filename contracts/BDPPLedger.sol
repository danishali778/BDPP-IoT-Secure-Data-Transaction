// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract BDPPLedger {
    address public owner;

    struct ReliabilityLog {
        bool reliable;
        uint256 errorScaled;
        uint256 timestamp;
    }

    struct TransactionLog {
        address buyer;
        uint256 price;
        string dataType;
        uint256 timestamp;
    }

    mapping(address => uint256) private userVersions;
    mapping(string => string) private cidRegistry;
    mapping(string => ReliabilityLog) private reliabilityLogs;
    mapping(string => TransactionLog) private transactionLogs;

    event UserRegistered(address indexed user, uint256 version);
    event UserRevoked(address indexed user, uint256 newVersion);
    event CIDStored(string indexed taskId, string cid);
    event ReliabilityLogged(string indexed taskId, bool reliable, uint256 errorScaled);
    event TransactionLogged(string indexed taskId, address indexed buyer, uint256 price, string dataType);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerUser(address user) external onlyOwner {
        if (userVersions[user] == 0) {
            userVersions[user] = 1;
            emit UserRegistered(user, 1);
        }
    }

    function revokeUser(address user) external onlyOwner {
        if (userVersions[user] == 0) {
            userVersions[user] = 1;
        }
        userVersions[user] += 1;
        emit UserRevoked(user, userVersions[user]);
    }

    function getUserVersion(address user) external view returns (uint256) {
        if (userVersions[user] == 0) {
            return 1;
        }
        return userVersions[user];
    }

    function storeCID(string calldata taskId, string calldata cid) external onlyOwner {
        cidRegistry[taskId] = cid;
        emit CIDStored(taskId, cid);
    }

    function getCID(string calldata taskId) external view returns (string memory) {
        return cidRegistry[taskId];
    }

    function logReliability(string calldata taskId, bool reliable, uint256 errorScaled) external onlyOwner {
        reliabilityLogs[taskId] = ReliabilityLog(reliable, errorScaled, block.timestamp);
        emit ReliabilityLogged(taskId, reliable, errorScaled);
    }

    function getReliability(string calldata taskId) external view returns (bool, uint256, uint256) {
        ReliabilityLog memory entry = reliabilityLogs[taskId];
        return (entry.reliable, entry.errorScaled, entry.timestamp);
    }

    function logTransaction(
        string calldata taskId,
        address buyer,
        uint256 price,
        string calldata dataType
    ) external onlyOwner {
        transactionLogs[taskId] = TransactionLog(buyer, price, dataType, block.timestamp);
        emit TransactionLogged(taskId, buyer, price, dataType);
    }

    function getTransaction(string calldata taskId) external view returns (address, uint256, string memory, uint256) {
        TransactionLog memory entry = transactionLogs[taskId];
        return (entry.buyer, entry.price, entry.dataType, entry.timestamp);
    }
}

