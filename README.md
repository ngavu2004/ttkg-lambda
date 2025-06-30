# Text-to-Knowledge Graph API Documentation

## Project Description

The **Text-to-Knowledge Graph API** is a serverless AI-powered solution that automatically transforms unstructured text and documents into interactive knowledge graphs. By leveraging advanced natural language processing through OpenAI's GPT-4, this API extracts entities (people, organizations, concepts) and their relationships from any text input, making complex information instantly more comprehensible and actionable.

**Key Features:**
- 🧠 **AI-Powered Analysis**: Uses GPT-4 via LangChain to intelligently identify entities and relationships
- 📄 **Multi-Format Support**: Processes direct text input and PDF document uploads
- 🔗 **Shareable Results**: Generates public links for knowledge graphs with expiration controls
- ⚡ **Serverless Architecture**: Built on AWS Lambda for automatic scaling and cost efficiency
- 🌐 **Developer-Friendly**: RESTful API with comprehensive CORS support for easy integration

**Use Cases:**
- Research paper analysis and academic literature mapping
- Business document processing and organizational knowledge extraction
- Content analysis for blogs, articles, and reports
- Educational material structuring and concept visualization
- Legal document relationship mapping

Transform your text into visual knowledge networks that reveal hidden connections and insights!

## Overview of Lambda Functions Usecase
The project uses **7 specialized Lambda functions** in a serverless microservices architecture, each handling specific tasks in the text-to-knowledge graph pipeline.

### 1. **HealchCheckFunction**
- **Input**: HTTP GET request
- **Output**: JSON health status message
- **Trigger**: API Gateway `/health_check` endpoint
- **Purpose**: System health monitoring

### 2. **KnowledgeGraphAPI** (Core AI Function)
- **Input**: JSON with text content `{"text": "..."}`
- **Output**: Knowledge graph with nodes and edges
- **Trigger**: API Gateway `/get_knowledge_graph` POST request
- **Purpose**: AI-powered text analysis using GPT-4 via LangChain

### 3. **PresignedURLFunction**
- **Input**: Query parameters (file_name, content_type)
- **Output**: S3 presigned upload URL and file_id
- **Trigger**: API Gateway `/get_presigned_url` GET request
- **Purpose**: Generate secure S3 upload URLs

### 4. **ProcessUploadedFunction** (File Processing Pipeline)
- **Input**: S3 event when PDF uploaded
- **Output**: Processed graph data stored in DynamoDB
- **Trigger**: S3 bucket object creation event (automatic)
- **Purpose**: Extract text from PDFs, invoke KnowledgeGraphAPI, save results

### 5. **GetSavedGraphFunction** (Polling Endpoint)
- **Input**: file_id path parameter
- **Output**: Processing status and graph data (if ready)
- **Trigger**: API Gateway `/get_saved_graph/{file_id}` GET request
- **Purpose**: Allow clients to poll for file processing completion

### 6. **GenerateShareLinkFunction**
- **Input**: JSON with graph_data and optional file_id
- **Output**: Shareable link with expiration
- **Trigger**: API Gateway `/generate-share-link` POST request
- **Purpose**: Create public shareable links for graphs

### 7. **ViewSharedGraphFunction**
- **Input**: share_id path parameter
- **Output**: Shared graph data and metadata
- **Trigger**: API Gateway `/view-graph/{share_id}` GET request
- **Purpose**: Retrieve graphs via public share links

## Key Architecture Features
Here's an ASCII architecture diagram for your Text-to-Knowledge Graph API:

```
# Text-to-Knowledge Graph API Architecture

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  Web Browser    │    Mobile App    │    API Client    │    HTML Test Page         │
│     ┌───┐       │      ┌───┐       │      ┌───┐       │       ┌───┐               │
│     │ 🌐 │       │      │ 📱 │       │      │ ⚙️ │       │       │ 🧪 │               │
│     └───┘       │      └───┘       │      └───┘       │       └───┘               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                    HTTPS/REST
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   API GATEWAY                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                            CORS Enabled                                    │   │
│  │  GET /health_check          POST /get_knowledge_graph                      │   │
│  │  GET /get_presigned_url     POST /generate-share-link                      │   │
│  │  GET /view-graph/{id}       GET /get_saved_graph/{file_id}                 │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                              Routes to Lambda Functions
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 LAMBDA FUNCTIONS                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────┐    ┌────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │HealthCheck   │    │KnowledgeGraph  │    │PresignedURL    │    │ProcessUploaded│ │
│  │Function      │    │API (Core AI)   │    │Function        │    │Function     │  │
│  │              │    │                │    │                │    │             │  │
│  │🏥 Health     │    │🧠 GPT-4 +      │    │🔗 S3 Upload   │    │📄 PDF       │  │
│  │   Monitoring │    │   LangChain    │    │   URLs        │    │   Processing │  │
│  │              │    │   Text→Graph   │    │                │    │             │  │
│  └──────────────┘    └────────────────┘    └─────────────────┘    └─────────────┘  │
│                              │                       │                    │        │
│                              │                       │                    │        │
│  ┌──────────────┐    ┌───────▼───────┐    ┌─────────▼───────┐    ┌───────▼─────┐  │
│  │GetSavedGraph │    │GenerateShare  │    │ViewSharedGraph  │    │   Layers    │  │
│  │Function      │    │LinkFunction   │    │Function         │    │             │  │
│  │              │    │               │    │                 │    │📦 ML Layer  │  │
│  │🔄 Polling    │    │🔗 Create      │    │👀 Retrieve     │    │   (AI Deps) │  │
│  │   Endpoint   │    │   Share Links │    │   Shared Graphs │    │             │  │
│  │              │    │               │    │                 │    │📦 Upload    │  │
│  └──────────────┘    └───────────────┘    └─────────────────┘    │   Layer     │  │
│                                                                   │   (PDF)     │  │
│                                                                   └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                  │                              │                         │
                  │                              │                         │
            Lambda Invocation                DynamoDB                      │
                  │                              │                         │
                  ▼                              ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATA LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────┐              ┌─────────────────────────────────────┐  │
│  │       DynamoDB          │              │              S3 Bucket              │  │
│  │   (GraphCacheTable)     │              │        (FileUploadBucket)           │  │
│  │                         │              │                                     │  │
│  │  🗃️ Graph Data Storage  │              │  📁 uploads/{file_id}/filename.pdf │  │
│  │                         │              │                                     │  │
│  │  Primary Key: share_id  │              │  🔄 Event Triggers:                │  │
│  │  GSI: file_id          │              │      Object Created →               │  │
│  │                         │              │      ProcessUploadedFunction        │  │
│  │  📊 Stored Data:        │              │                                     │  │
│  │   • Graph nodes/edges   │              │  🌐 CORS Enabled                   │  │
│  │   • Share links         │              │   • Direct file uploads            │  │
│  │   • Expiration (TTL)    │              │   • Presigned URL support          │  │
│  │   • View counts         │              │                                     │  │
│  │   • File metadata       │              │                                     │  │
│  └─────────────────────────┘              └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────┐              ┌─────────────────────────────────────┐  │
│  │      OpenAI GPT-4       │              │        AWS Secrets Manager         │  │
│  │                         │              │                                     │  │
│  │  🤖 AI Language Model   │              │  🔐 Secure API Key Storage         │  │
│  │   • Entity extraction   │              │   • OpenAI API key                  │  │
│  │   • Relationship mapping│              │   • Encrypted at rest              │  │
│  │   • Text understanding  │              │   • IAM-controlled access          │  │
│  │                         │              │                                     │  │
│  └─────────────────────────┘              └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘

                            📊 DATA FLOW EXAMPLES

1. TEXT PROCESSING FLOW:
   Client → API Gateway → KnowledgeGraphAPI → OpenAI GPT-4 → Response

2. FILE UPLOAD FLOW:
   Client → PresignedURLFunction → S3 Upload → S3 Event → ProcessUploadedFunction 
        → KnowledgeGraphAPI → DynamoDB Storage

3. POLLING FLOW:
   Client → GetSavedGraphFunction → DynamoDB Query → Status Response

4. SHARE LINK FLOW:
   Client → GenerateShareLinkFunction → DynamoDB Storage → Share URL
   Anyone → ViewSharedGraphFunction → DynamoDB Retrieval → Graph Data

                            🏗️ KEY ARCHITECTURE FEATURES

• Serverless: All compute via Lambda functions (no servers to manage)
• Event-Driven: S3 uploads automatically trigger processing
• Microservices: Each function has single responsibility
• Scalable: Auto-scales from 0 to 1000+ concurrent executions
• Cost-Effective: Pay only for actual usage
• Secure: IAM roles, API Gateway, encrypted secrets
• CORS-Enabled: Direct browser access from any domain
• Stateless: All state in DynamoDB and S3
```


## Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/Prod
```

## Authentication

**No Authentication Required**: All endpoints are currently publicly accessible.

**Headers Required:**
```
Content-Type: application/json
```

**Example Request:**
```javascript
const response = await fetch('/get_knowledge_graph', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
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
console.log('Nodes:', data.nodes);
console.log('Edges:', data.edges);
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
  "upload_url": "https://bucket.s3.amazonaws.com/uploads/uuid/filename.pdf?signature=...",
  "file_name": "document.pdf",
  "file_id": "12345678-1234-1234-1234-123456789abc"
}
```

**Example Request:**
```javascript
const response = await fetch('/get_presigned_url?file_name=resume.pdf&content_type=application/pdf');
const data = await response.json();

// Use the presigned URL to upload file
const uploadResponse = await fetch(data.upload_url, {
  method: 'PUT',
  body: fileBlob,
  headers: {
    'Content-Type': 'application/pdf'
  }
});
```

---

### 4. Get Saved Graph by File ID
**GET** `/get_saved_graph/{file_id}`

Retrieve the processed knowledge graph for an uploaded file.

**Path Parameters:**
- `file_id`: The unique identifier returned from the presigned URL request

**Response (Processing - 404 Not Found):**
```json
{
  "status": "Processing",
  "message": "Graph not found or being processed. Please try again in a few moments."
}
```

**Response (Completed):**
```json
{
  "status": "completed",
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
  "view_count": 1
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Detailed error message"
}
```

**Example Request:**
```javascript
const fileId = "12345678-1234-1234-1234-123456789abc";

const response = await fetch(`/get_saved_graph/${fileId}`);
const result = await response.json();

if (result.status === "completed") {
  console.log('Graph data:', result.graph_data);
} else if (result.status === "processing") {
  console.log('Still processing, try again later');
} else {
  console.error('Processing failed:', result.error);
}
```

---

### 5. Generate Shareable Link
**POST** `/generate-share-link`

Create a shareable link for a knowledge graph.

**Headers:**
```
Content-Type: application/json
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
const response = await fetch('/generate-share-link', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
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

### 6. View Shared Graph
**GET** `/view-graph/{share_id}`

Retrieve a shared knowledge graph using its share ID.

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
const shareId = "87654321-4321-4321-4321-abcdef123456";

const response = await fetch(`/view-graph/${shareId}`);
const sharedGraph = await response.json();
console.log('Graph nodes:', sharedGraph.graph_data.nodes);
console.log('Graph edges:', sharedGraph.graph_data.edges);
```

---

## Complete Workflow Examples

### API Client Setup
```javascript
class TTKGApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
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
const client = new TTKGApiClient(API_BASE_URL);
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
    
    console.log('File ID:', urlData.file_id);
    
    // Step 2: Upload file to S3
    const uploadResponse = await fetch(urlData.upload_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type }
    });
    
    if (!uploadResponse.ok) {
      throw new Error('File upload failed');
    }
    
    console.log('File uploaded successfully, processing started...');
    
    // Step 3: Poll for processing completion
    const graphData = await pollForProcessingCompletion(urlData.file_id);
    
    return {
      file_id: urlData.file_id,
      graph_data: graphData
    };
    
  } catch (error) {
    console.error('Error in file workflow:', error);
    throw error;
  }
}

async function pollForProcessingCompletion(fileId, maxAttempts = 30, intervalMs = 2000) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      console.log(`Checking processing status (attempt ${attempt}/${maxAttempts})...`);
      
      const response = await fetch(`${client.baseUrl}/get_saved_graph/${fileId}`);
      
      if (response.status === 200) {
        // Success - graph data is ready
        const result = await response.json();
        console.log('Processing completed successfully!');
        console.log('Graph contains:', result.graph_data.nodes?.length || 0, 'nodes and', result.graph_data.edges?.length || 0, 'edges');
        return result.graph_data;
      } else if (response.status === 404) {
        // File not found or not processed yet
        console.log('File not ready yet, waiting...');
        
        // Wait before next attempt
        if (attempt < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, intervalMs));
        }
      } else if (response.status === 500) {
        // Server error - might be temporary
        const errorResult = await response.json();
        console.log(`Server error (attempt ${attempt}): ${errorResult.error}`);
        
        if (attempt < maxAttempts) {
          // Wait longer for server errors
          await new Promise(resolve => setTimeout(resolve, intervalMs * 2));
        } else {
          throw new Error(`Processing failed with server error: ${errorResult.error}`);
        }
      } else {
        // Other HTTP errors - usually not recoverable
        const errorResult = await response.json();
        throw new Error(`HTTP ${response.status}: ${errorResult.error || 'Unknown error'}`);
      }
    } catch (error) {
      if (error.name === 'TypeError' && attempt < maxAttempts) {
        // Network error - retry
        console.log(`Network error (attempt ${attempt}): ${error.message}, retrying...`);
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        continue;
      }
      
      if (attempt === maxAttempts) {
        throw new Error(`Polling failed after ${maxAttempts} attempts: ${error.message}`);
      }
      
      throw error; // Re-throw non-network errors immediately
    }
  }
  
  throw new Error(`Processing timeout: file did not complete processing after ${maxAttempts} attempts`);
}

// Usage
// Usage with enhanced error handling
async function handleFileUpload(fileInput) {
  const file = fileInput.files[0];
  if (!file) {
    alert('Please select a file');
    return;
  }
  
  try {
    console.log('Starting file upload and processing...');
    
    // Show loading indicator
    const loadingElement = document.getElementById('loading');
    if (loadingElement) loadingElement.style.display = 'block';
    
    const result = await uploadAndProcessFile(file);
    
    console.log('File processed successfully!');
    console.log('File ID:', result.file_id);
    console.log('Graph data:', result.graph_data);
    
    // Hide loading indicator
    if (loadingElement) loadingElement.style.display = 'none';
    
    // Display results
    displayGraphData(result.graph_data);
    
    return result;
  } catch (error) {
    console.error('File processing failed:', error);
    
    // Hide loading indicator
    const loadingElement = document.getElementById('loading');
    if (loadingElement) loadingElement.style.display = 'none';
    
    // Show user-friendly error message
    let userMessage = 'File processing failed. ';
    if (error.message.includes('timeout')) {
      userMessage += 'The file is taking longer than expected to process. Please try again later.';
    } else if (error.message.includes('Network')) {
      userMessage += 'Please check your internet connection and try again.';
    } else {
      userMessage += error.message;
    }
    
    alert(userMessage);
  }
}
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

### 5. Complete File-to-Share Workflow
```javascript
async function completeFileWorkflow(file) {
  try {
    // 1. Upload and process file
    console.log('Step 1: Uploading and processing file...');
    const fileResult = await uploadAndProcessFile(file);
    
    // 2. Create shareable link
    console.log('Step 2: Creating share link...');
    const shareUrl = await shareGraph(fileResult.file_id, fileResult.graph_data);
    
    // 3. Return complete result
    return {
      file_id: fileResult.file_id,
      graph_data: fileResult.graph_data,
      share_url: shareUrl,
      message: 'File processed and share link created successfully!'
    };
    
  } catch (error) {
    console.error('Complete workflow failed:', error);
    throw error;
  }
}

// Usage
const result = await completeFileWorkflow(selectedFile);
console.log('Workflow completed:', result);
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

## File Processing Status

When uploading files, the processing follows these stages:

### Status Types:
1. **`processing`** - File is being analyzed and knowledge graph is being extracted
2. **`completed`** - Processing finished successfully, graph data available
3. **`error`** - Processing failed, error message provided

### Polling Strategy:
- **Initial wait**: 2-5 seconds after upload before first poll
- **Poll interval**: Every 2-3 seconds
- **Timeout**: Stop polling after 60 seconds (30 attempts)
- **Exponential backoff**: Consider increasing intervals for longer files

### Processing Time Estimates:
- **Small text files** (< 1MB): 5-15 seconds
- **PDF documents** (1-10MB): 15-60 seconds  
- **Large documents** (> 10MB): 1-3 minutes

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

**File Processing Errors**
```json
{
  "status": "error",
  "error": "Unsupported file type. Please upload PDF, TXT, or DOCX files."
}
```

---

## CORS Headers

All endpoints include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: content-type
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

---

## Supported File Types

The API currently supports:
- **PDF files** (.pdf)
- **Text files** (.txt) 
- **Word documents** (.docx) - *planned*

**File Size Limits:**
- Maximum file size: 50MB
- Maximum text length after extraction: 100,000 characters

---

## Notes

1. **File Processing**: After uploading a file, use the returned `file_id` to poll the `/get_saved_graph/{file_id}` endpoint until processing completes

2. **Polling Best Practice**: Wait 2-3 seconds between polling attempts to avoid overwhelming the API

3. **Share Link Expiration**: Share links expire after 30 days by default

4. **No Authentication**: Currently all endpoints are publicly accessible

5. **Maximum Text Length**: Large texts are automatically chunked (2000 characters with 200 character overlap)

6. **CORS Support**: The API supports cross-origin requests from any domain

7. **Graph Format**: The API returns `nodes` and `edges` (not `relationships`) in the format described in the Graph Schema section

8. **Processing Timeout**: If polling times out, the file may still be processing - try polling again later

9. **Async Processing**: File processing happens asynchronously, so upload success doesn't guarantee processing success
```

## Key Changes Made:

1. **Removed API Key Authentication** - Updated all sections to reflect that no authentication is currently required
2. **Updated File Upload Workflow** - Now shows the complete workflow with polling using `file_id`
3. **Added Get Saved Graph Endpoint** - Documented the `/get_saved_graph/{file_id}` endpoint with all possible responses
4. **Enhanced Polling Examples** - Provided comprehensive polling logic with error handling, timeouts, and retry strategies
5. **Added Processing Status Section** - Detailed explanation of processing stages and timing expectations
6. **Updated Workflow Examples** - Complete end-to-end examples showing file upload → poll → share link creation
7. **Corrected Response Format** - Fixed the presigned URL response to show `upload_url` instead of `presigned_url`
8. **Added File Processing Guidelines** - Information about supported file types, size limits, and processing times

The README now accurately reflects your current API setup without authentication and shows the proper workflow for file uploads with polling! 🎉## Key Changes Made:

1. **Removed API Key Authentication** - Updated all sections to reflect that no authentication is currently required
2. **Updated File Upload Workflow** - Now shows the complete workflow with polling using `file_id`
3. **Added Get Saved Graph Endpoint** - Documented the `/get_saved_graph/{file_id}` endpoint with all possible responses
4. **Enhanced Polling Examples** - Provided comprehensive polling logic with error handling, timeouts, and retry strategies
5. **Added Processing Status Section** - Detailed explanation of processing stages and timing expectations
6. **Updated Workflow Examples** - Complete end-to-end examples showing file upload → poll → share link creation
7. **Corrected Response Format** - Fixed the presigned URL response to show `upload_url` instead of `presigned_url`
8. **Added File Processing Guidelines** - Information about supported file types, size limits, and processing times

The README now accurately reflects your current API setup without authentication and shows the proper workflow for file uploads with polling! 🎉