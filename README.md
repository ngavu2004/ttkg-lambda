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

const response = await fetch(`/view-graph/${