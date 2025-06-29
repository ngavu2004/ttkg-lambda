# Text-to-Knowledge Graph API Documentation

## Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/Prod
```

## Authentication

**API Key Required**: All endpoints require an API key for access.

**Headers Required:**
```
X-Api-Key: your-api-key-here
Content-Type: application/json
```

**Example Request with API Key:**
```javascript
const response = await fetch('/get_knowledge_graph', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key-here'
  },
  body: JSON.stringify({
    text: "Your text content here..."
  })
});
```

---

## API Endpoints

### 1. Health Check
**GET** `/health_check`

Check if the API is running.

**Headers:**
```
X-Api-Key: your-api-key-here
```

**Response:**
```json
{
  "message": "API is healthy",
  "timestamp": "2025-06-29T10:30:00Z"
}
```

---

### 2. Generate Knowledge Graph from Text
**POST** `/get_knowledge_graph`

Extract knowledge graph from provided text using AI.

**Headers:**
```
Content-Type: application/json
X-Api-Key: your-api-key-here
```

**Request Body:**
```json
{
  "text": "Your text content here..."
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "John Doe",
      "type": "John Doe",
      "properties": {}
    },
    {
      "id": "Microsoft",
      "type": "Microsoft",
      "properties": {}
    },
    {
      "id": "Software Engineer",
      "type": "Software Engineer",
      "properties": {}
    }
  ],
  "edges": [
    {
      "source": "John Doe",
      "target": "Microsoft",
      "type": "WORKS_AT"
    },
    {
      "source": "John Doe",
      "target": "Software Engineer",
      "type": "HAS_ROLE"
    }
  ]
}
```

**Example Request:**
```javascript
const API_KEY = 'your-api-key-here';

const response = await fetch('/get_knowledge_graph', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': API_KEY
  },
  body: JSON.stringify({
    text: "John Doe works at Microsoft as a software engineer. He graduated from Stanford University."
  })
});

const data = await response.json();
console.log('Nodes:', data.nodes);
console.log('Edges:', data.edges);
```

---

### 3. Get Presigned URL for File Upload
**GET** `/get_presigned_url`

Get a presigned URL to upload files directly to S3.

**Headers:**
```
X-Api-Key: your-api-key-here
```

**Query Parameters:**
- `file_name` (optional): Name of the file
- `content_type` (optional): MIME type of the file (default: application/octet-stream)

**Response:**
```json
{
  "presigned_url": "https://bucket.s3.amazonaws.com/uploads/uuid/filename.pdf?signature=...",
  "file_name": "document.pdf",
  "file_id": "12345678-1234-1234-1234-123456789abc"
}
```

**Example Request:**
```javascript
const API_KEY = 'your-api-key-here';

const response = await fetch('/get_presigned_url?file_name=resume.pdf&content_type=application/pdf', {
  headers: {
    'X-Api-Key': API_KEY
  }
});
const data = await response.json();

// Use the presigned URL to upload file (no API key needed for S3 upload)
const uploadResponse = await fetch(data.presigned_url, {
  method: 'PUT',
  body: fileBlob,
  headers: {
    'Content-Type': 'application/pdf'
  }
});
```

---

### 4. Generate Shareable Link
**POST** `/generate-share-link`

Create a shareable link for a knowledge graph.

**Headers:**
```
Content-Type: application/json
X-Api-Key: your-api-key-here
```

**Request Body:**
```json
{
  "file_id": "12345678-1234-1234-1234-123456789abc",
  "graph_data": {
    "nodes": [
      {
        "id": "John Doe",
        "type": "Person",
        "properties": {}
      }
    ],
    "edges": [
      {
        "source": "John Doe",
        "target": "Microsoft",
        "type": "WORKS_AT"
      }
    ]
  }
}
```

**Response:**
```json
{
  "share_id": "87654321-4321-4321-4321-abcdef123456",
  "share_url": "https://api.example.com/Prod/view-graph/87654321-4321-4321-4321-abcdef123456",
  "expires_at": 1719820800
}
```

**Example Request:**
```javascript
const API_KEY = 'your-api-key-here';

const response = await fetch('/generate-share-link', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': API_KEY
  },
  body: JSON.stringify({
    file_id: "file-uuid-here",
    graph_data: {
      nodes: [
        { "id": "John Doe", "type": "Person", "properties": {} },
        { "id": "Microsoft", "type": "Company", "properties": {} }
      ],
      edges: [
        { "source": "John Doe", "target": "Microsoft", "type": "WORKS_AT" }
      ]
    }
  })
});

const shareData = await response.json();
console.log("Share URL:", shareData.share_url);
```

---

### 5. View Shared Graph
**GET** `/view-graph/{share_id}`

Retrieve a shared knowledge graph using its share ID.

**Headers:**
```
X-Api-Key: your-api-key-here
```

**Path Parameters:**
- `share_id`: The unique identifier for the shared graph

**Response:**
```json
{
  "graph_data": {
    "nodes": [
      {
        "id": "John Doe",
        "type": "Person",
        "properties": {}
      }
    ],
    "edges": [
      {
        "source": "John Doe",
        "target": "Microsoft",
        "type": "WORKS_AT"
      }
    ]
  },
  "file_id": "12345678-1234-1234-1234-123456789abc",
  "created_at": "2025-06-29T10:30:00Z",
  "view_count": 5
}
```

**Example Request:**
```javascript
const API_KEY = 'your-api-key-here';
const shareId = "87654321-4321-4321-4321-abcdef123456";

const response = await fetch(`/view-graph/${shareId}`, {
  headers: {
    'X-Api-Key': API_KEY
  }
});
const sharedGraph = await response.json();
console.log('Graph nodes:', sharedGraph.graph_data.nodes);
console.log('Graph edges:', sharedGraph.graph_data.edges);
```

---

## Complete Workflow Examples

### API Client Setup
```javascript
class TTKGApiClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': this.apiKey,
        ...options.headers
      }
    };

    const requestOptions = { ...defaultOptions, ...options };
    const response = await fetch(url, requestOptions);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// Initialize client
const API_BASE_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod';
const API_KEY = 'your-api-key-here';
const client = new TTKGApiClient(API_BASE_URL, API_KEY);
```

### 1. Text-to-Graph Workflow
```javascript
async function generateGraphFromText(text) {
  try {
    const graphData = await client.makeRequest('/get_knowledge_graph', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
    
    // Process nodes and edges
    console.log('Extracted nodes:', graphData.nodes);
    console.log('Extracted edges:', graphData.edges);
    
    return graphData;
  } catch (error) {
    console.error('Error generating graph:', error);
    throw error;
  }
}

// Usage
const graph = await generateGraphFromText("Your text here...");
```

### 2. File Upload and Processing Workflow
```javascript
async function uploadAndProcessFile(file) {
  try {
    // Step 1: Get presigned URL
    const urlData = await client.makeRequest(
      `/get_presigned_url?file_name=${encodeURIComponent(file.name)}&content_type=${encodeURIComponent(file.type)}`
    );
    
    // Step 2: Upload file to S3 (no API key needed for this step)
    const uploadResponse = await fetch(urlData.presigned_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type }
    });
    
    if (!uploadResponse.ok) {
      throw new Error('File upload failed');
    }
    
    return {
      file_id: urlData.file_id,
      message: 'File uploaded successfully. Processing will begin automatically.'
    };
    
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}

// Usage
const result = await uploadAndProcessFile(fileInput.files[0]);
```

### 3. Share Graph Workflow
```javascript
async function shareGraph(fileId, graphData) {
  try {
    // Ensure graphData has the correct format with nodes and edges
    const shareData = await client.makeRequest('/generate-share-link', {
      method: 'POST',
      body: JSON.stringify({
        file_id: fileId,
        graph_data: {
          nodes: graphData.nodes,  // Array of node objects
          edges: graphData.edges   // Array of edge objects
        }
      })
    });
    
    return shareData.share_url;
  } catch (error) {
    console.error('Error creating share link:', error);
    throw error;
  }
}

// Usage with correct schema
const shareUrl = await shareGraph("file-id", {
  nodes: [
    { "id": "John Doe", "type": "Person", "properties": {} }
  ],
  edges: [
    { "source": "John Doe", "target": "Microsoft", "type": "WORKS_AT" }
  ]
});
```

### 4. View Shared Graph Workflow
```javascript
async function viewSharedGraph(shareId) {
  try {
    const sharedData = await client.makeRequest(`/view-graph/${shareId}`);
    return sharedData;
  } catch (error) {
    if (error.message.includes('404')) {
      throw new Error('Graph not found or expired');
    }
    console.error('Error viewing shared graph:', error);
    throw error;
  }
}

// Usage
const sharedGraph = await viewSharedGraph("share-id-here");
```

---

## Graph Schema

### Node Object
```json
{
  "id": "string",        // Unique identifier for the node
  "type": "string",      // Type/category of the node (often same as id)
  "properties": {}       // Additional properties (currently empty object)
}
```

### Edge Object  
```json
{
  "source": "string",    // ID of the source node
  "target": "string",    // ID of the target node  
  "type": "string"       // Type of relationship (e.g., "WORKS_AT", "LOCATED_IN")
}
```

### Complete Graph Data Structure
```json
{
  "nodes": [
    {
      "id": "Entity Name",
      "type": "Entity Type", 
      "properties": {}
    }
  ],
  "edges": [
    {
      "source": "Source Entity ID",
      "target": "Target Entity ID",
      "type": "RELATIONSHIP_TYPE"
    }
  ]
}
```

**Common Relationship Types:**
- `WORKS_AT` - Employment relationship
- `LOCATED_IN` - Geographic relationship  
- `STUDIED` - Educational relationship
- `HAS_ROLE` - Role/position relationship
- `GRADUATED_FROM` - Educational completion
- `SPECIALIZES_IN` - Area of expertise

---

## Error Responses

All endpoints may return these common error responses:

**401 Unauthorized (Missing or Invalid API Key)**
```json
{
  "message": "Unauthorized"
}
```

**403 Forbidden (API Key Valid but Access Denied)**
```json
{
  "message": "Forbidden"
}
```

**400 Bad Request**
```json
{
  "error": "Missing required parameter: text"
}
```

**404 Not Found**
```json
{
  "error": "Graph not found or expired"
}
```

**500 Internal Server Error**
```json
{
  "error": "Internal server error message"
}
```

---

## CORS Headers

All endpoints include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type, X-Api-Key
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

---

## Rate Limits

The API includes rate limiting through usage plans:

- **Rate Limit**: 100 requests per second
- **Burst Limit**: 200 requests
- **Daily Quota**: 10,000 requests per day

When rate limits are exceeded, you'll receive a `429 Too Many Requests` response.

---

## Security Best Practices

### 1. API Key Storage
```javascript
// ❌ Don't hardcode API keys in frontend code
const API_KEY = 'your-api-key-here';

// ✅ Use environment variables
const API_KEY = process.env.REACT_APP_TTKG_API_KEY;

// ✅ Or fetch from secure storage
const API_KEY = await getApiKeyFromSecureStorage();
```

### 2. Error Handling
```javascript
async function makeSecureRequest(endpoint, options = {}) {
  try {
    const response = await client.makeRequest(endpoint, options);
    return response;
  } catch (error) {
    if (error.message.includes('401') || error.message.includes('403')) {
      // Handle authentication errors
      console.error('Authentication failed. Please check your API key.');
      // Redirect to login or refresh API key
    }
    throw error;
  }
}
```

### 3. API Key Validation
```javascript
function validateApiKey(apiKey) {
  if (!apiKey || apiKey.length < 20) {
    throw new Error('Invalid API key format');
  }
  return true;
}
```

---

## Getting Your API Key

After deploying the application, retrieve your API key:

```bash
# Get API key from CloudFormation outputs
aws cloudformation describe-stacks \
  --stack-name text-to-kg \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiKey`].OutputValue' \
  --output text

# Get API base URL
aws cloudformation describe-stacks \
  --stack-name text-to-kg \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiBaseUrl`].OutputValue' \
  --output text
```

---

## Notes

1. **File Processing**: After uploading a file, processing happens automatically. The knowledge graph will be saved to S3 at `uploads/{file_id}/knowledge_graph.json`

2. **Share Link Expiration**: Share links expire after 30 days by default

3. **Supported File Types**: Currently supports PDF files for automatic processing

4. **Maximum Text Length**: Large texts are automatically chunked (2000 characters with 200 character overlap)

5. **Authentication**: **API key required for all endpoints** - ensure your frontend securely stores and transmits the API key

6. **CORS**: The API supports cross-origin requests from any domain, but requires a valid API key

7. **Rate Limiting**: Monitor your usage to stay within the daily quota limits

8. **Graph Format**: The API returns `nodes` and `edges` (not `relationships`) in the format described in the Graph Schema section
```

The key updates include:
1. **Added API key authentication section** at the top
2. **Updated all endpoint examples** to include `X-Api-Key` header
3. **Corrected the graph schema** to use `nodes` and `edges` with proper object format
4. **Added security best practices** for API key handling
5. **Updated error responses** to include authentication errors
6. **Added rate limiting information**
7. **Updated CORS headers** to include `X-Api-Key`
8. **Added instructions** for obtaining API keysThe key updates include:
1. **Added API key authentication section** at the top
2. **Updated all endpoint examples** to include `X-Api-Key` header
3. **Corrected the graph schema** to use `nodes` and `edges` with proper object format
4. **Added security best practices** for API key handling
5. **Updated error responses** to include authentication errors
6. **Added rate limiting information**
7. **Updated CORS headers** to include `X-Api-Key`
8. **Added instructions** for obtaining API keys