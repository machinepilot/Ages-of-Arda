typedef enum {
    MCP_MSG_EVENT = 1,
    MCP_MSG_QUERY = 2,
    MCP_MSG_RESPONSE = 3,
    MCP_MSG_COMMAND = 4,
    MCP_MSG_HEARTBEAT = 5,
    MCP_MSG_ERROR = 6
} mcp_message_type_t;

typedef struct {
    uint32_t magic;           // Magic number for validation (MCP1)
    uint16_t version;         // Protocol version
    uint16_t message_type;    // Type of message
    uint32_t sequence;        // Sequence number
    uint32_t payload_length;  // Length of the following JSON payload
    uint64_t timestamp;       // Message timestamp
    uint16_t flags;           // Protocol flags
    uint16_t reserved;        // Reserved for future use
    // Followed by payload_length bytes of JSON data
} mcp_message_header_t; 