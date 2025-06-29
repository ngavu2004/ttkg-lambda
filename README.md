# Text-to-Knowledge Graph API Documentation

## Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/Prod
```

## API Endpoints

### 1. Health Check
**GET** `/health_check`

Check if the API is running.

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
    ["Entity Name", "Entity Type"],
    ["John Doe", "Person"],
    ["Microsoft", "Organization"]
  ],
  "relationships": [
    ["Source Entity", "Target Entity", "Relationship Type"],
    ["John Doe", "Microsoft", "WORKS_AT"]
  ]
}
```

**Example Request:**
```javascript
const response = await fetch('/get_knowledge_graph', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: "John Doe works at Microsoft as a software engineer. He graduated from Stanford University."
  })
});

const data = await response.json();
console.log(data);
```

---

### 3. Get Presigned URL for File Upload
**GET** `/get_presigned_url`

Get a presigned URL to upload files directly to S3.

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
const response = await fetch('/get_presigned_url?file_name=resume.pdf&content_type=application/pdf');
const data = await response.json();

// Use the presigned URL to upload file
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

**Request Body:**
```json
{
  "file_id": "12345678-1234-1234-1234-123456789abc",
  "graph_data": {
    "nodes": [["Entity", "Type"]],
    "relationships": [["Source", "Target", "Relation"]]
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
const response = await fetch('/generate-share-link', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    file_id: "file-uuid-here",
    graph_data: {
      nodes: [["John Doe", "Person"], ["Microsoft", "Company"]],
      relationships: [["John Doe", "Microsoft", "WORKS_AT"]]
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

**Path Parameters:**
- `share_id`: The unique identifier for the shared graph

**Response:**
```json
{
  "graph_data": {
    "nodes": [["Entity", "Type"]],
    "relationships": [["Source", "Target", "Relation"]]
  },
  "file_id": "12345678-1234-1234-1234-123456789abc",
  "created_at": "2025-06-29T10:30:00Z",
  "view_count": 5
}
```

**Example Request:**
```javascript
const shareId = "87654321-4321-4321-4321-abcdef123456";
const response = await fetch(`/view-graph/${shareId}`);
const sharedGraph = await response.json();
console.log(sharedGraph.graph_data);
```

---

## Complete Workflow Examples

### 1. Text-to-Graph Workflow
```javascript
async function generateGraphFromText(text) {
  try {
    const response = await fetch('/get_knowledge_graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const graphData = await response.json();
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
    const urlResponse = await fetch(`/get_presigned_url?file_name=${file.name}&content_type=${file.type}`);
    const urlData = await urlResponse.json();
    
    // Step 2: Upload file to S3
    const uploadResponse = await fetch(urlData.presigned_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type }
    });
    
    if (!uploadResponse.ok) {
      throw new Error('File upload failed');
    }
    
    // Step 3: File will be automatically processed
    // You can poll or wait for processing completion
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
    const response = await fetch('/generate-share-link', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_id: fileId,
        graph_data: graphData
      })
    });
    
    const shareData = await response.json();
    return shareData.share_url;
  } catch (error) {
    console.error('Error creating share link:', error);
    throw error;
  }
}

// Usage
const shareUrl = await shareGraph("file-id", graphData);
```

### 4. View Shared Graph Workflow
```javascript
async function viewSharedGraph(shareId) {
  try {
    const response = await fetch(`/view-graph/${shareId}`);
    
    if (response.status === 404) {
      throw new Error('Graph not found or expired');
    }
    
    const sharedData = await response.json();
    return sharedData;
  } catch (error) {
    console.error('Error viewing shared graph:', error);
    throw error;
  }
}

// Usage
const sharedGraph = await viewSharedGraph("share-id-here");
```

---

## Error Responses

All endpoints may return these common error responses:

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
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

---

## Rate Limits

- Text-to-graph API: Limited by Lambda concurrency and OpenAI API limits
- File uploads: Standard S3 limits apply
- Share links: No specific rate limits

---

## Notes

1. **File Processing**: After uploading a file, processing happens automatically. The knowledge graph will be saved to S3 at `uploads/{file_id}/knowledge_graph.json`

2. **Share Link Expiration**: Share links expire after 30 days by default

3. **Supported File Types**: Currently supports PDF files for automatic processing

4. **Maximum Text Length**: Large texts are automatically chunked (2000 characters with 200 character overlap)

5. **Authentication**: Currently no authentication required (adjust based on your security needs)