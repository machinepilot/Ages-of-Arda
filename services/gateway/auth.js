const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// HMAC for message verification
function generateMessageHMAC(message, secret) {
    return crypto.createHmac('sha256', secret)
                 .update(JSON.stringify(message))
                 .digest('hex');
}

// Token-based authentication for MCP clients
function generateClientToken(clientId, permissions) {
    return jwt.sign(
        { 
            clientId, 
            permissions,
            iat: Math.floor(Date.now() / 1000)
        },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
}

// Middleware to verify client requests
function verifyClientMiddleware(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Unauthorized: No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.client = decoded;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Unauthorized: Invalid token' });
    }
} 