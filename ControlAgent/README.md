# Threat-Intelligence-Analysis-Agentic-AI-App

# Threat Intelligence Analysis

How to run : $ docker run -d -p 9002:9002 --name fastapi-container --env-file .env fastapi-v1


1] The **Threat Intelligence Analysis** project is a comprehensive tool for gathering, analyzing, and assessing the threat level of IP addresses and malware samples. It combines geographical, reputation, and threat data to provide actionable insights into cyber risks. The application leverages various tools and APIs to provide geolocation information, threat scores, and malware analysis summaries.

 2] Engineered a modular Threat Intelligence Analysis platform using Python and Streamlit, integrating VirusTotal
and IPInfo APIs to perform real-time threat assessment and geolocation analysis of suspicious IPs and malware
hashes.

 3] Implemented an AI-powered analysis system using LangChain and Google’s Gemini Pro model to automate threat
scoring and risk assessment, reducing manual analysis time by leveraging React and Plan-Execute agents.

4] Developed a comprehensive threat scoring algorithm that evaluates multiple risk factors including geographical
location, organizational context, and historical threat data to generate actionable security insights.

### Key Components

1. **Geolocate_IP**: 
   - Uses the IPInfo API to retrieve geographical details about an IP address.
   - Provides city, region, country, coordinates, and organization.
   - Requires an API key set in the `.env` file.

2. **Threat_Score_Assessment**: 
   - Calculates a comprehensive threat score based on:
     - Malicious samples data from VirusTotal.
     - Geographical risk, including high-risk countries.
     - Suspicious hosting/cloud organizations.
   - Generates a risk assessment: Low, Medium, or High.

3. **Malware_Analysis_Summary**: 
   - Provides detailed summaries of malware characteristics from VirusTotal.
   - Includes detection rates, first/last seen dates, and type tags.
  
### Tool Build

- Use Geolocate_IP to get geographical context
- Use Retrieve_IP_Info to find associated malicious samples
- Use Threat_Score_Assessment to calculate overall risk
- If samples exist, use Retrieve_Hash_Information to get sample details
- Use Malware_Analysis_Summary for comprehensive malware analysis


### Features

- **Geolocation Information**: Accurate details of the geographical location of IP addresses.
- **Threat Scoring**: Calculate threat levels based on a combination of multiple data sources.
- **Malware Hash Analysis**: Retrieve detailed information about malware samples and their associated risks.
- **IP Reputation Assessment**: Assess the reputation and risk level of IP addresses in real-time.

### Limitations

- **External API Dependency**: Relies on external APIs (such as IPInfo and VirusTotal), which could be unavailable or rate-limited.
- **Contextual Understanding**: Limited contextual understanding, as the analysis is based on available data only.
- **Performance Issues**: May experience delays with complex or bulk queries.
- **Data Quality Variability**: The data quality may vary across different sources.

### Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Prathameshchakote/Threat-Intelligence-Analysis-Agentic-AI-App.git
   cd Threat-Intelligence-Analysis-Agentic-AI-App
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.7 or higher installed, then install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your IPInfo API key:
   ```
   IPINFO_API_KEY=your_ipinfo_api_key
   ```

4. **Run the Application**:
   - For a streamlit UI interface, run:
     ```bash
     streamlit run ui/streamlit_app.py
     ```
   - To run the application from the command line, use:
     ```bash
     python app.py
     ```

### Example Queries

**1. IP Address Intelligence Queries**:
- *"What threat information can you find about the IP 77.246.107.91?"*
- *"Analyze the geolocation and potential risks of IP 8.8.8.8"*
- *"Provide a comprehensive threat assessment for the IP 104.16.88.20"*

**2. Malware Hash Analysis**:
- *"Can you retrieve details about the malware hash 44d88612fea8a8f36de82e1278abb02f?"*
- *"Analyze the threat level and characteristics of hash abc123def456"*
- *"Get malware sample information for 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"*

**3. Threat Score Calculation**:
- *"Calculate the threat score for IP 185.153.196.90"*
- *"Assess the risk level of IP 45.133.193.72"*
- *"Provide a detailed threat intelligence report for 104.21.78.63"*

**4. Comprehensive Threat Intelligence**:
- *"Perform a full threat analysis on the IP 185.220.101.42"*
- *"Investigate potential risks associated with 5.255.96.133"*
- *"Provide a complete threat intelligence breakdown for 91.121.93.41"*

### Future Enhancements

- Integrate additional data sources for better coverage and accuracy.
- Improve query handling and error management for better user experience.
- Expand the user interface to display detailed analysis in a more structured format.
