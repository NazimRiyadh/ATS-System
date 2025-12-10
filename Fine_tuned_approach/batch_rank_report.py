import asyncio
import os
from rank_candidates import get_ranked_candidates

JDS = [
    {
        "title": "Business Development Manager",
        "description": """BUSINESS-DEVELOPMENT 
Job Title: Business Development Manager  
Location: Hybrid – Dhaka, Bangladesh  
Employment Type: Full-time  

About the Role  
The Business Development Manager will drive revenue growth by identifying new markets, building strategic partnerships, and expanding our client portfolio in the B2B technology space.  

Key Responsibilities  
- Identify, qualify, and prioritize new business opportunities through market research, outbound prospecting, and networking.  
- Build and manage a robust sales pipeline; prepare proposals, quotations, and RFP responses.  
- Negotiate commercial terms and close deals in collaboration with finance and legal teams.  
- Maintain strong relationships with key accounts, ensuring upsell and cross‑sell opportunities.  
- Track and report monthly/quarterly performance metrics (pipeline, win rate, revenue) to leadership.  

Required Skills & Qualifications  
- Bachelor’s degree in Business, Marketing, or related field.  
- 3–5 years’ experience in B2B sales or business development, ideally in SaaS or IT services.  
- Strong negotiation, presentation, and stakeholder‑management skills.  
- Proficiency with CRM tools (e.g., HubSpot, Salesforce) and Excel/Sheets for pipeline reporting.  

Nice to Have  
- Experience selling into US/EU markets.  
- Familiarity with solution or consultative selling methodologies.  

Compensation  
- Typical salary range (market reference): USD 35,000–60,000/year + performance‑based commission, depending on location and experience."""
    },
    {
        "title": "Digital Media Specialist",
        "description": """DIGITAL-MEDIA
Job Title: Digital Media Specialist  
Location: Remote (Global)  
Employment Type: Full-time  

About the Role  
The Digital Media Specialist will plan, execute, and optimize multi‑channel campaigns to grow brand awareness, traffic, and conversions across paid and organic digital channels.  

Key Responsibilities  
- Develop and manage campaigns across social media, search, display, and video platforms (Meta, Google Ads, YouTube, TikTok, LinkedIn).  
- Create and localize ad copies, basic creatives, and landing page briefs in collaboration with designers and content teams.  
- Set up tracking (UTM, pixels, conversion events) and monitor campaign performance in Google Analytics and platform dashboards.  
- Optimize bids, audiences, and creatives based on KPIs such as CTR, CPC, CPA, and ROAS.  
- Prepare weekly and monthly performance reports with actionable insights and testing roadmaps.  

Required Skills & Qualifications  
- Bachelor’s degree in Marketing, Communications, or related field.  
- 2–4 years of hands‑on experience running paid and organic campaigns.  
- Strong knowledge of Meta Ads Manager, Google Ads, and Google Analytics/GA4.  
- Data‑driven mindset with solid Excel/Sheets skills (pivot tables, basic formulas).  

Nice to Have  
- Experience with marketing automation tools (e.g., HubSpot, Mailchimp).  
- Basic HTML/CSS familiarity for landing page tweaks.  

Compensation  
- Typical salary range: USD 40,000–70,000/year, depending on geography and experience."""
    },
    {
        "title": "General Engineer (Product/Systems)",
        "description": """ENGINEERING 
Job Title: General Engineer (Product/Systems)  
Location: On-site – Berlin, Germany  
Employment Type: Full-time  

About the Role  
The General Engineer will support the design, analysis, and improvement of mechanical and electro‑mechanical systems used in our industrial products, working closely with cross‑functional R&D and manufacturing teams.  

Key Responsibilities  
- Design components and assemblies using CAD tools; prepare drawings and specifications.  
- Perform calculations, tolerance analyses, and basic simulations (FEA or equivalent) to validate designs.  
- Support prototype builds, testing, root‑cause analysis, and design iterations.  
- Collaborate with suppliers and manufacturing to ensure designs are cost‑effective and manufacturable.  
- Maintain design documentation, risk analyses, and compliance records (safety, regulatory standards).  

Required Skills & Qualifications  
- Bachelor’s degree in Mechanical, Mechatronics, or related Engineering discipline.  
- 2–5 years’ experience in product or systems engineering.  
- Proficiency in at least one major CAD package (SolidWorks, CATIA, Inventor, or similar).  
- Familiarity with engineering standards and basic reliability/safety concepts.  

Nice to Have  
- Experience with FEA tools, DFMEA, or design for manufacturability.  
- Exposure to PLCs, embedded systems, or industrial automation.  

Compensation  
- Typical salary range: EUR 55,000–85,000/year plus bonus, depending on level and location."""
    },
    {
        "title": "HR Generalist",
        "description": """HR
Job Title: HR Generalist  
Location: Hybrid – Bangalore, India  
Employment Type: Full-time  

About the Role  
The HR Generalist will own day‑to‑day HR operations, supporting employees and managers across recruitment, onboarding, performance, and engagement for a 200–400‑person organization.  

Key Responsibilities  
- Manage end‑to‑end recruitment for selected roles: JD creation, sourcing, screening, coordination, and offer processes.  
- Oversee onboarding, documentation, HRIS updates, and probation confirmations.  
- Support performance‑management cycles, goal‑setting, and basic capability‑building programs.  
- Handle employee queries, grievances, and policy clarifications, escalating complex issues when required.  
- Maintain HR analytics dashboards (headcount, attrition, diversity, leave, etc.) and ensure statutory compliance.  

Required Skills & Qualifications  
- Bachelor’s degree; MBA/PGDM in HR preferred.  
- 2–4 years’ experience in a generalist or HR operations role.  
- Solid knowledge of labor laws and HR best practices relevant to the region.  
- Strong communication, counseling, and stakeholder‑management skills.  

Compensation  
- Typical salary range: equivalent of USD 20,000–40,000/year (local currency adjusted), depending on market and seniority."""
    },
    {
        "title": "IT Specialist / Systems Engineer",
        "description": """INFORMATION-TECHNOLOGY 
Job Title: IT Specialist / Systems Engineer  
Location: On-site – London, UK  
Employment Type: Full-time  
About the Role  
The IT Specialist will be responsible for supporting end‑user devices, servers, and network infrastructure, ensuring secure and reliable IT services for a mid‑sized organization.  

Key Responsibilities  
- Install, configure, and maintain laptops, servers, operating systems, and business applications.  
- Monitor system and network health; troubleshoot incidents (L1/L2) and coordinate with vendors for complex issues.  
- Administer identity and access (AD/Azure AD), email, collaboration tools, and backups.  
- Implement security patches, antivirus, and endpoint protection policies as per guidelines.  
- Document procedures, maintain asset inventories, and contribute to IT improvement projects.  

Required Skills & Qualifications  
- Diploma or Bachelor’s in Computer Science, Information Technology, or related field.  
- 2–5 years’ experience in IT support or systems administration.  
- Hands‑on experience with Windows/Linux administration, networking basics, and ticketing tools.  

Nice to Have  
- Certifications such as CompTIA A+/Network+, Microsoft, or similar.  
- Experience with cloud platforms (Azure, AWS, or GCP).  

Compensation  
- Typical salary range: GBP 30,000–55,000/year plus benefits, depending on experience and certifications."""
    }
]

async def generate_report():
    report_content = "# ATS Candidate Ranking Report\n\n"
    report_content += "This report summarizes the top 5 candidates for each of the 5 provided Job Descriptions.\n\n"
    
    for i, jd in enumerate(JDS):
        title = jd['title']
        description = jd['description']
        print(f"\nProcessing JD {i+1}/{len(JDS)}: {title}...")
        
        candidates = await get_ranked_candidates(description, top_k=5)
        
        report_content += f"## {i+1}. {title}\n\n"
        
        if not candidates:
            report_content += "**No suitable candidates found.**\n\n"
        else:
            report_content += "| Rank | Score | Name | Source File | Key Skills Matched | Evidence |\n"
            report_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            
            for cand in candidates:
                rank = cand.get('rank', '-')
                score = f"{cand.get('match_score', 0)}%"
                name = cand.get('name', 'N/A')
                source = cand.get('source_file', 'N/A')
                skills = ", ".join(cand.get('skills_matched', []))
                evidence = cand.get('evidence', 'N/A').replace('\n', ' ')
                
                report_content += f"| {rank} | {score} | {name} | {source} | {skills} | {evidence} |\n"
            
            report_content += "\n"
            
        report_content += "---\n\n"
        
    with open("ranking_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("\nReport generated: ranking_report.md")

if __name__ == "__main__":
    asyncio.run(generate_report())
