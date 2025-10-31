# Data Sources for Policy Navigator Agent

## Primary Data Sources (US Government)

### 1. Code of Federal Regulations (CFR) - XML Format
**Source:** National Archives and Records Administration (NARA)  
**URL:** https://www.govinfo.gov/bulkdata/CFR/  
**Format:** XML  
**Coverage:** 1996 to present  
**Update Frequency:** Quarterly  
**Description:** The CFR is the codification of the general and permanent rules published in the Federal Register by executive departments and agencies. It is divided into 50 titles representing broad areas subject to Federal regulation.

**Data Access:**
- Bulk downloads available by year, title, and volume
- XML structured files derived from SGML-tagged data
- Current data available at: https://www.govinfo.gov/app/collection/cfr/

**Legal Status:** Only PDF and Text versions have official legal status. XML is provided for convenience.

### 2. Federal Register API
**Source:** National Archives and Records Administration (NARA)  
**URL:** https://www.federalregister.gov/developers/documentation/api/v1  
**Format:** JSON API  
**Description:** Daily publication of federal regulations, proposed rules, notices, and executive orders.

**Key Endpoints:**
- `/api/v1/documents.json` - Search and retrieve documents
- `/api/v1/documents/{document_number}.json` - Get specific document
- `/api/v1/public-inspection-documents.json` - Documents on public inspection

**Features:**
- Real-time access to Federal Register documents
- Search by agency, date, document type
- Full text search capabilities
- No API key required for basic usage

### 3. Regulations.gov API
**Source:** General Services Administration (GSA)  
**URL:** https://open.gsa.gov/api/regulationsgov/  
**Format:** REST API  
**Description:** Access to federal regulatory documents, comments, and dockets.

**Key Features:**
- Search regulations and comments
- Access docket information
- Retrieve agency information
- API key required (free registration)

### 4. EPA Regulations and Data
**Source:** U.S. Environmental Protection Agency  
**URL:** https://www.epa.gov/data  
**Formats:** CSV, JSON, XML, API  
**Description:** Environmental regulations, compliance data, and enforcement information.

**Key Datasets:**
- ECHO (Enforcement and Compliance History Online)
- Envirofacts data system
- Air quality regulations
- Water quality standards
- Hazardous waste regulations

**Data Downloads:**
- https://www.epa.gov/enviro/data-downloads
- https://echo.epa.gov/tools/data-downloads

### 5. Electronic Code of Federal Regulations (e-CFR)
**Source:** National Archives and Records Administration (NARA)  
**URL:** https://www.ecfr.gov/  
**Format:** XML, HTML  
**Description:** Up-to-date, unofficial version of the CFR updated daily.

**API Access:**
- XML bulk data: https://www.ecfr.gov/developers/documentation/api/v1
- Real-time updates
- Title and part level access

## Secondary Data Sources

### 6. CourtListener API (Case Law)
**Source:** Free Law Project  
**URL:** https://www.courtlistener.com/api/  
**Format:** REST API  
**Description:** Federal and state court opinions, dockets, and oral arguments.

**Key Features:**
- Search court opinions
- Link regulations to case law
- Access to Supreme Court and Circuit Court decisions
- API key required (free registration)

### 7. Data.gov Compliance Datasets
**URL:** https://catalog.data.gov/dataset/?tags=compliance  
**Description:** Various compliance and regulatory datasets from federal agencies.

## Website Sources for Scraping

### 1. EPA Regulations Website
**URL:** https://www.epa.gov/laws-regulations  
**Content:** Environmental laws, regulations, and guidance documents

### 2. FDA Regulations
**URL:** https://www.fda.gov/regulatory-information  
**Content:** Food, drug, and medical device regulations

### 3. OSHA Standards
**URL:** https://www.osha.gov/laws-regs  
**Content:** Occupational safety and health standards

### 4. CDC Guidelines
**URL:** https://www.cdc.gov/policy/  
**Content:** Public health guidelines and policies

## Data Collection Strategy

### Phase 1: Initial Dataset (Static)
1. Download CFR XML files for key titles:
   - Title 40: Protection of Environment (EPA)
   - Title 21: Food and Drugs (FDA)
   - Title 29: Labor (OSHA)
   - Title 42: Public Health (CDC)

2. Parse XML and extract:
   - Regulation text
   - Section numbers
   - Effective dates
   - Agency information

### Phase 2: Dynamic Data (API Integration)
1. Federal Register API:
   - Check for new regulations
   - Track amendments and updates
   - Monitor executive orders

2. Regulations.gov API:
   - Access public comments
   - Track regulatory dockets
   - Monitor agency actions

### Phase 3: Case Law Integration
1. CourtListener API:
   - Link regulations to court cases
   - Retrieve relevant opinions
   - Track legal challenges

### Phase 4: Website Scraping
1. EPA website scraping:
   - Guidance documents
   - Fact sheets
   - Technical resources

2. Agency-specific content:
   - Policy statements
   - Interpretive guidance
   - Compliance assistance

## Vector Database Strategy

### Document Processing
1. **Chunking Strategy:**
   - Split by regulation section (e.g., § 40.1, § 40.2)
   - Maintain section hierarchy
   - Keep metadata (title, part, section, agency)

2. **Embedding Model:**
   - Use sentence-transformers or OpenAI embeddings
   - Embed regulation text with metadata

3. **Vector Storage:**
   - ChromaDB for local development
   - Persistent storage for production

4. **Metadata Schema:**
   ```json
   {
     "title": "40",
     "part": "60",
     "section": "1",
     "agency": "EPA",
     "effective_date": "2024-01-01",
     "source": "CFR",
     "url": "https://...",
     "last_updated": "2024-10-31"
   }
   ```

## API Keys Required

1. **aiXplain API Key:** Already obtained (3e0b********1e2e)
2. **Federal Register API:** No key required
3. **Regulations.gov API:** Required (free) - https://open.gsa.gov/api/regulationsgov/
4. **CourtListener API:** Required (free) - https://www.courtlistener.com/api/
5. **Slack API (optional):** For notifications - https://api.slack.com/

## Data Update Schedule

- **CFR:** Quarterly (matches official publication schedule)
- **Federal Register:** Daily (via API)
- **Regulations.gov:** Real-time (via API)
- **Case Law:** Weekly (via CourtListener API)
- **Website Scraping:** Weekly or on-demand

## Compliance Notes

- All data sources are US Government public domain or openly accessible
- Proper attribution will be provided in responses
- API rate limits will be respected
- Terms of service for each API will be followed
