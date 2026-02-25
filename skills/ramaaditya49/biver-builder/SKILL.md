# 🚀 Biver Public API Documentation (v1.0.1)

Welcome to the **Biver API** — the public REST API for the Biver landing page builder platform.
This documentation is designed for **developers and AI agents** who want to integrate
Biver's services into their applications.

---

## 📚 Table of Contents

1. [Getting Started](#-getting-started)
2. [Authentication](#-authentication)
3. [Base URL & Endpoints](#-base-url--endpoints)
4. [Rate Limits](#-rate-limits)
5. [API Endpoints Reference](#-api-endpoints-reference)
6. [Error Handling](#-error-handling)
7. [Examples](#-examples)

---

## 🚀 Getting Started

### Don't Have an Account Yet?

If you do not have a Biver account, follow these steps:

1. Go to [https://biver.id](https://biver.id) and click **Sign Up**
2. Register using your email or Google account
3. After logging in, you will be prompted to create a **Workspace** (this represents your business/project)
4. Once your workspace is created, you are ready to generate an API Key

### How to Get Your API Key

1. Log in to the Biver dashboard at [https://biver.id](https://biver.id)
2. Open the **Settings** page from the sidebar
3. Navigate to the **API Keys** tab
4. Click **Generate New Key**
5. Give it a descriptive name (e.g. "My AI Integration")
6. Select the scopes (permissions) you need
7. Click **Create** — your API key will be shown **once only**. Copy and store it securely!

> ⚠️ **Important:** The full API key is only displayed at creation time. If you lose it, you must generate a new one.

### Make Your First Request

```bash
curl -X GET \
  'https://api.biver.id/v1/pages' \
  -H 'X-API-Key: bvr_live_xxxxx'
```

Or using a Bearer token:

```bash
curl -X GET \
  'https://api.biver.id/v1/pages' \
  -H 'Authorization: Bearer bvr_live_xxxxx'
```

---

## 🔐 Authentication

The Biver API uses **API Key** authentication. Every request must include your API key.

### Header Options

You can use either of the following headers:

| Header | Format | Example |
|--------|--------|---------|
| `X-API-Key` | `{prefix}_{key}` | `bvr_live_a1b2c3d4...` |
| `Authorization` | `Bearer {prefix}_{key}` | `Bearer bvr_live_a1b2c3d4...` |

### API Key Prefixes

| Prefix | Environment | Description |
|--------|-------------|-------------|
| `bvr_live_` | Production | For real/production data |
| `bvr_test_` | Sandbox | For testing (does not affect real data) |

### Scopes (Permissions)

Each API key has scopes that restrict its access:

| Scope | Description |
|-------|-------------|
| `pages:read` | Read-only access to pages |
| `pages:write` | Create, update, delete pages |
| `sections:read` | Read-only access to sections |
| `sections:write` | Create, update, delete sections |
| `products:read` | Read-only access to products |
| `products:write` | Manage product catalog |
| `forms:read` | Read form submissions |
| `forms:write` | Create/update forms |
| `gallery:read` | Access gallery assets |
| `domains:read` | View custom domains |
| `domains:write` | Add/remove custom domains |
| `subdomains:read` | View subdomains |
| `subdomains:write` | Create/update/delete subdomains |
| `workspace:read` | Read workspace settings |
| `workspace:write` | Update workspace settings |
| `ai:generate` | Generate pages/sections with AI |

---

## 🌐 Base URL & Endpoints

### Base URL

```
https://api.biver.id
```

### Available Endpoints

#### Health Check (No Auth Required)
```
GET /health
```

#### Pages API
```
GET    /v1/pages              # List all pages
POST   /v1/pages              # Create a new page
GET    /v1/pages/:id          # Get page details
PATCH  /v1/pages/:id          # Update a page
DELETE /v1/pages/:id          # Delete a page
POST   /v1/pages/:id/deploy   # Deploy (publish) a page
```

#### Sections API
```
GET    /v1/sections           # List sections
POST   /v1/sections           # Create a section
GET    /v1/sections/:id       # Get section details
PATCH  /v1/sections/:id       # Update a section
DELETE /v1/sections/:id       # Delete a section
```

#### Products API
```
GET    /v1/products           # List products
POST   /v1/products           # Create a product
GET    /v1/products/:id       # Get product details
PATCH  /v1/products/:id       # Update a product
DELETE /v1/products/:id       # Delete a product
```

#### Forms API
```
GET    /v1/forms              # List forms
POST   /v1/forms              # Create a form
GET    /v1/forms/:id          # Get form details
PATCH  /v1/forms/:id          # Update a form
DELETE /v1/forms/:id          # Delete a form
POST   /v1/forms/:id/submit   # Submit a form (public, no auth)
GET    /v1/forms/:id/submissions  # Get form submissions
```

#### Gallery API
```
GET    /v1/gallery            # List gallery items
POST   /v1/gallery            # Upload an asset
GET    /v1/gallery/:id        # Get asset details
DELETE /v1/gallery/:id        # Delete an asset
```

#### Domains API (Custom Domains)
```
GET    /v1/domains            # List custom domains
POST   /v1/domains            # Add a custom domain
GET    /v1/domains/:id        # Get domain details
PATCH  /v1/domains/:id        # Update domain settings
DELETE /v1/domains/:id        # Remove a custom domain
POST   /v1/domains/:id/primary  # Set as primary domain
```

#### Subdomains API
```
GET    /v1/subdomains         # List subdomains
POST   /v1/subdomains         # Create a subdomain
GET    /v1/subdomains/:id     # Get subdomain details
PATCH  /v1/subdomains/:id     # Update a subdomain
DELETE /v1/subdomains/:id     # Delete a subdomain
```

> **Subdomain format:** All subdomains use the format `{name}.lp.biver.id`.
> For example, if you create a subdomain called `my-store`, it will be accessible at `my-store.lp.biver.id`.
> You can also set a **path slug** (e.g. `promo-sale`) so the page is accessible at `my-store.lp.biver.id/promo-sale`.

#### Workspace API
```
GET    /v1/workspace/settings   # Get workspace settings
PUT    /v1/workspace/settings   # Update workspace settings
PUT    /v1/workspace/branding   # Update branding settings
PUT    /v1/workspace/seo        # Update SEO settings
GET    /v1/workspace/public     # Get public workspace info
```

#### AI Generation API
```
POST   /v1/ai/pages           # Generate a page with AI
POST   /v1/ai/sections        # Generate a section with AI
GET    /v1/ai/context          # Get AI context/templates
```

---

## ⏱️ Rate Limits

Request limits per minute based on your subscription plan:

| Plan | Requests/Minute | Description |
|------|-----------------|-------------|
| SCOUT | 30 | Free-tier users |
| CRAFTSMAN | 60 | Small businesses |
| ARCHITECT | 120 | Growing businesses |
| ENGINEER | 300 | Medium businesses |
| FOUNDER | 600 | Agencies |
| CHIEF | 2000 | Enterprise |

### Rate Limit Headers

Every response includes rate limit information headers:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1708704000000
X-RateLimit-Plan: CRAFTSMAN
```

---

## 📖 API Endpoints Reference

### Pages API

#### List Pages
```http
GET /v1/pages?page=1&limit=10&status=published
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number for pagination |
| `limit` | number | 10 | Items per page (max 100) |
| `status` | string | - | Filter: `draft`, `published`, `archived` |
| `search` | string | - | Search by page title |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "page_123",
        "title": "Summer Sale Landing Page",
        "slug": "summer-sale",
        "status": "published",
        "publishedAt_ms": 1708704000000,
        "createdAt_ms": 1708617600000
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

#### Create Page
```http
POST /v1/pages
```

**Request Body:**
```json
{
  "title": "New Landing Page",
  "slug": "new-landing",
  "content": {
    "sections": []
  },
  "meta": {
    "description": "SEO description for the page",
    "keywords": "keyword1, keyword2"
  },
  "status": "draft"
}
```

#### Get Page Detail
```http
GET /v1/pages/:id
```

#### Update Page
```http
PATCH /v1/pages/:id
```

#### Delete Page
```http
DELETE /v1/pages/:id
```

#### Deploy (Publish) Page
```http
POST /v1/pages/:id/deploy
```

Changes the page status from `draft` to `published` and sets the `publishedAt_ms` timestamp.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "page_123",
    "title": "Summer Sale Landing Page",
    "slug": "summer-sale",
    "status": "published",
    "publishedAt_ms": 1708704000000,
    "updatedAt_ms": 1708704000000,
    "createdAt_ms": 1708617600000
  }
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `NOT_FOUND` | Page not found |
| `DEPLOY_FAILED` | Failed to deploy |

---

### Sections API

#### List Sections
```http
GET /v1/sections?page=1&limit=20&type=hero
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter: `hero`, `features`, `pricing`, etc. |
| `pageId` | string | Filter sections by page ID |

#### Create Section
```http
POST /v1/sections?pageId=page_123
```

**Request Body:**
```json
{
  "type": "hero",
  "name": "Hero Section",
  "htmlContent": "<div class="hero"><h1>Welcome to Our Store</h1><p>Discover amazing products</p><a href="#products" class="btn">Shop Now</a></div>",
  "cssContent": ".hero { text-align: center; padding: 4rem 2rem; } .btn { background: #3B82F6; color: white; padding: 0.75rem 1.5rem; }",
  "visible": true,
  "order": 0
}
```

**Section Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Section type: `hero`, `text`, `image`, `image_slider`, `faq`, etc. |
| `name` | string | Yes | Section name for identification |
| `htmlContent` | string | No | HTML content of the section |
| `cssContent` | string | No | CSS styles for the section |
| `visible` | boolean | No | Whether section is visible (default: true) |
| `order` | number | No | Display order (default: 0) |
| `customClass` | string | No | Custom CSS class |
| `anchorId` | string | No | ID for anchor links (e.g., #hero) |

---

### Products API

#### List Products
```http
GET /v1/products?page=1&limit=10&category=electronics
```

#### Create Product
```http
POST /v1/products
```

**Request Body:**
```json
{
  "name": "Sample Product",
  "description": "Full product description",
  "price": 99000,
  "compareAtPrice": 149000,
  "sku": "PROD-001",
  "stock": 100,
  "category": "electronics",
  "images": ["url1", "url2"],
  "isActive": true
}
```

---

### Forms API

#### List Forms
```http
GET /v1/forms
```

#### Get Form Submissions
```http
GET /v1/forms/:id/submissions?page=1&limit=50
```

#### Submit Form (Public — No Auth Required)
```http
POST /v1/forms/:id/submit
```

**Request Body:**
```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello, I'm interested in your services..."
  }
}
```

---

### Gallery API

#### List Gallery Items
```http
GET /v1/gallery?page=1&limit=20&type=image
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | `image`, `video`, `document` |
| `search` | string | Search by filename |

#### Get Gallery Item
```http
GET /v1/gallery/:id
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "gallery_123",
    "filename": "hero-image.png",
    "url": "https://cdn.biver.id/assets/xxx.png",
    "type": "image",
    "mimeType": "image/png",
    "size": 102400,
    "width": 1920,
    "height": 1080,
    "createdAt_ms": 1708704000000
  }
}
```

---

### Domains API (Custom Domains)

Custom domains allow you to serve your landing pages from your own domain name (e.g. `example.com`).

#### List Custom Domains
```http
GET /v1/domains
```

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "domain_123",
        "domain": "example.com",
        "isPrimary": true,
        "isVerified": true,
        "sslStatus": "active",
        "verificationStatus": "verified",
        "landingPageId": "page_123",
        "createdAt_ms": 1708704000000
      }
    ]
  }
}
```

#### Add a Custom Domain
```http
POST /v1/domains
```

**Request Body:**
```json
{
  "domain": "example.com",
  "isPrimary": true,
  "landingPageId": "page_123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | Yes | The custom domain name (e.g. `example.com`) |
| `isPrimary` | boolean | No | Set as the primary domain for this workspace |
| `landingPageId` | string (UUID) | No | Link this domain to a specific landing page |

> **Slug on custom domains:** The linked landing page's `pathSlug` determines the URL path.
> For example, if your landing page has `pathSlug: "promo"`, it will be accessible at `example.com/promo`.

#### Get Domain Detail
```http
GET /v1/domains/:id
```

**Response includes DNS verification records:**
```json
{
  "success": true,
  "data": {
    "id": "domain_123",
    "domain": "example.com",
    "isPrimary": true,
    "isVerified": true,
    "sslStatus": "active",
    "verificationStatus": "verified",
    "verificationToken": "bvr_verify_xxx",
    "landingPageId": "page_123",
    "createdAt_ms": 1708704000000
  }
}
```

#### Update Domain
```http
PATCH /v1/domains/:id
```

**Request Body:**
```json
{
  "isPrimary": false,
  "landingPageId": "page_456"
}
```

#### Delete Domain
```http
DELETE /v1/domains/:id
```

#### Set Primary Domain
```http
POST /v1/domains/:id/primary
```

Marks this domain as the primary domain for the workspace. Any previously primary domain will be unset.

---

### Subdomains API

Subdomains allow you to create landing pages accessible at `{name}.lp.biver.id`.
Each subdomain is essentially a landing page entry with a unique subdomain name.

#### List Subdomains
```http
GET /v1/subdomains?page=1&limit=20&status=published
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | number | 1 | Page number for pagination |
| `limit` | number | 20 | Items per page (max 100) |
| `status` | string | - | Filter: `draft`, `published`, `archived` |

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "lp_abc123",
        "subdomain": "my-store",
        "fullDomain": "my-store.lp.biver.id",
        "title": "My Store Landing Page",
        "slug": "my-store-landing-page",
        "pathSlug": "promo",
        "status": "published",
        "createdAt_ms": 1708704000000
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "totalPages": 1
    }
  }
}
```

> In the above example, the page is accessible at both:
> - `my-store.lp.biver.id` (root)
> - `my-store.lp.biver.id/promo` (with path slug)

#### Create Subdomain
```http
POST /v1/subdomains
```

**Request Body:**
```json
{
  "subdomain": "my-store",
  "title": "My Store Landing Page",
  "description": "Official landing page for my store",
  "pathSlug": "summer-sale"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subdomain` | string | Yes | Subdomain name (3-63 chars, lowercase a-z, 0-9, hyphens). The full URL will be `{subdomain}.lp.biver.id` |
| `title` | string | Yes | Page title (max 255 chars) |
| `description` | string | No | Page description (max 2000 chars) |
| `pathSlug` | string | No | URL path segment (2-100 chars, lowercase, hyphens allowed). If set, the page is also accessible at `{subdomain}.lp.biver.id/{pathSlug}` |

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "lp_abc123",
    "subdomain": "my-store",
    "fullDomain": "my-store.lp.biver.id",
    "title": "My Store Landing Page",
    "slug": "my-store-landing-page",
    "pathSlug": "summer-sale",
    "description": "Official landing page for my store",
    "status": "draft",
    "createdAt_ms": 1708704000000,
    "updatedAt_ms": 1708704000000
  }
}
```

#### Get Subdomain Detail
```http
GET /v1/subdomains/:id
```

#### Update Subdomain
```http
PATCH /v1/subdomains/:id
```

**Request Body:**
```json
{
  "title": "Updated Page Title",
  "pathSlug": "new-promo",
  "status": "published",
  "metaTitle": "SEO Title for My Page",
  "metaDescription": "SEO description for search engines",
  "noIndex": false,
  "noFollow": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Update page title |
| `description` | string | Update page description |
| `pathSlug` | string or null | Set or clear the URL path slug. Set to `null` to remove it |
| `status` | string | `draft`, `published`, or `archived` |
| `metaTitle` | string | SEO meta title |
| `metaDescription` | string | SEO meta description |
| `favicon` | string (URL) | Favicon URL |
| `ogImage` | string (URL) | Open Graph image URL |
| `noIndex` | boolean | Prevent search engine indexing |
| `noFollow` | boolean | Prevent search engine link following |

#### Delete Subdomain
```http
DELETE /v1/subdomains/:id
```

---

### Workspace API

#### Get Workspace Settings
```http
GET /v1/workspace/settings
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "workspace_123",
    "name": "My Workspace",
    "slug": "my-workspace",
    "plan": "ARCHITECT",
    "settings": {
      "timezone": "Asia/Jakarta",
      "language": "en",
      "currency": "USD"
    },
    "branding": {
      "logo": "https://cdn.biver.id/logos/xxx.png",
      "primaryColor": "#3B82F6",
      "fontFamily": "Inter"
    },
    "seo": {
      "title": "My Business",
      "description": "We build great landing pages",
      "keywords": "landing page, builder",
      "ogImage": "https://cdn.biver.id/og/xxx.png"
    },
    "createdAt_ms": 1708704000000
  }
}
```

#### Update Workspace Settings
```http
PUT /v1/workspace/settings
```

**Request Body:**
```json
{
  "name": "My Updated Workspace",
  "settings": {
    "timezone": "Asia/Jakarta",
    "language": "en",
    "currency": "USD"
  }
}
```

#### Update Branding Settings
```http
PUT /v1/workspace/branding
```

**Request Body:**
```json
{
  "logo": "https://cdn.biver.id/logos/new.png",
  "primaryColor": "#10B981",
  "fontFamily": "Poppins"
}
```

#### Update SEO Settings
```http
PUT /v1/workspace/seo
```

**Request Body:**
```json
{
  "title": "My Business - Landing Page Builder",
  "description": "Create beautiful landing pages in minutes",
  "keywords": "landing page, builder, no-code",
  "ogImage": "https://cdn.biver.id/og/new.png"
}
```

#### Get Public Workspace Info
```http
GET /v1/workspace/public
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "My Workspace",
    "slug": "my-workspace",
    "branding": {
      "logo": "https://cdn.biver.id/logos/xxx.png",
      "primaryColor": "#3B82F6"
    }
  }
}
```

---

### AI Generation API

#### Generate Page with AI
```http
POST /v1/ai/pages
```

**Request Body:**
```json
{
  "prompt": "Create a landing page for a modern coffee shop called 'Morning Brew' with a warm and cozy theme",
  "style": "modern",
  "industry": "fnb",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Morning Brew - Premium Coffee Experience",
    "content": {
      "sections": [...]
    },
    "suggestedSlug": "morning-brew"
  }
}
```

#### Generate Section with AI
```http
POST /v1/ai/sections
```

**Request Body:**
```json
{
  "pageId": "page_123",
  "type": "features",
  "prompt": "Create a features section for a coffee shop highlighting: premium beans, cozy atmosphere, free wifi",
  "language": "en"
}
```

#### Get AI Context
```http
GET /v1/ai/context
```

Returns available templates and context for AI generation.

---

## ⚠️ Error Handling

### Error Response Format

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description | How to Fix |
|------|-------------|-------------|------------|
| `UNAUTHORIZED` | 401 | API key is invalid or missing | Check your authentication header |
| `KEY_EXPIRED` | 401 | API key has expired | Generate a new API key from the dashboard |
| `KEY_REVOKED` | 401 | API key has been revoked | Generate a new API key from the dashboard |
| `FORBIDDEN` | 403 | API key does not have the required permission | Check the scopes on your API key |
| `NOT_FOUND` | 404 | The requested resource was not found | Verify the resource ID |
| `DUPLICATE_SUBDOMAIN` | 409 | The subdomain name is already taken | Choose a different subdomain name |
| `DUPLICATE_DOMAIN` | 409 | The domain already exists in the workspace | Use a different domain |
| `VALIDATION_ERROR` | 422 | The request body failed validation | Check the request body format and required fields |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait for the reset window or upgrade your plan |
| `INTERNAL_ERROR` | 500 | Internal server error | Try again later or contact support |

### Validation Error Example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "title",
          "message": "Title is required",
          "code": "required"
        },
        {
          "field": "price",
          "message": "Price must be a positive number",
          "code": "min"
        }
      ]
    }
  }
}
```

---

## 💡 Examples

### Example 1: Create a Landing Page with a Subdomain

```typescript
// Step 1: Create a subdomain with a path slug
const createSubdomain = async () => {
  const response = await fetch('https://api.biver.id/v1/subdomains', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'bvr_live_xxxxx'
    },
    body: JSON.stringify({
      subdomain: 'my-store',
      title: 'Summer Sale 2026',
      description: 'Our biggest sale of the year',
      pathSlug: 'summer-sale'
    })
  });

  const data = await response.json();
  console.log('Created:', data.data.fullDomain);
  // Output: "Created: my-store.lp.biver.id"
  // Accessible at: my-store.lp.biver.id/summer-sale
};
```

### Example 2: Add a Custom Domain

```typescript
const addDomain = async () => {
  // Step 1: Add the custom domain
  const response = await fetch('https://api.biver.id/v1/domains', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'bvr_live_xxxxx'
    },
    body: JSON.stringify({
      domain: 'my-store.com',
      isPrimary: true,
      landingPageId: 'page_123'  // Link to an existing landing page
    })
  });

  const data = await response.json();
  console.log('Domain added:', data.data.domain);
  console.log('Verification token:', data.data.verificationToken);
  // Configure your DNS with the verification token
};
```

### Example 3: Generate a Page with AI

```typescript
const generatePage = async () => {
  const response = await fetch('https://api.biver.id/v1/ai/pages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'bvr_live_xxxxx'
    },
    body: JSON.stringify({
      prompt: 'Create a landing page for a SaaS product management tool called TaskFlow',
      style: 'modern',
      industry: 'saas',
      language: 'en'
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Generated page:', data.data.title);
    console.log('Sections:', data.data.sections?.length || 0);
  }
};
```

### Example 4: Paginated Listing

```typescript
const getAllPages = async () => {
  let page = 1;
  const limit = 50;
  const allPages = [];

  while (true) {
    const response = await fetch(
      `https://api.biver.id/v1/pages?page=${page}&limit=${limit}`,
      {
        headers: {
          'X-API-Key': 'bvr_live_xxxxx'
        }
      }
    );

    const data = await response.json();

    if (!data.success) break;

    allPages.push(...data.data.items);

    if (page >= data.data.pagination.totalPages) break;
    page++;
  }

  return allPages;
};
```

### Example 5: Submit a Public Form (No Auth Required)

```typescript
const submitForm = async (formId: string, formData: object) => {
  const response = await fetch(
    `https://api.biver.id/v1/forms/${formId}/submit`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // No API key needed for public form submissions!
      },
      body: JSON.stringify({ data: formData })
    }
  );

  return response.json();
};
```

---

## 📞 Support

If you need help:

1. **Documentation**: Visit this page at `GET /docs` or `GET /SKILL.md`
2. **Dashboard**: [https://biver.id/dashboard](https://biver.id/dashboard)
3. **Email**: support@biver.id

---

*This documentation is auto-generated and always up-to-date.*
*Last updated: 2026-02-24*
