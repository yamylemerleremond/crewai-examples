# Warning control
import warnings
warnings.filterwarnings('ignore')
import os
import yaml
import asyncio
from crewai import Agent, Task, Crew

from crewai import Flow
from crewai.flow.flow import Flow, listen, start, and_, or_
from sales_pipeline.crews.lead_enrichment.src.lead_enrichment.crew import LeadEnrichment
from sales_pipeline.crews.email_writing.src.email_writing.crew import EmailWriting


class SalesPipeline(Flow):
    @start()
    def fetch_leads(self):
        # Pull our leads from the database
        leads = [
            {
                "lead_data": {
                    "name": "Anne Pernet",
                    "job_title": "Directrice CRM",
                    "company": "Veolia Environnement",
                    "email": "anne@veolia.fr",
                    "use_case": "Using AI Agent to do better data enrichment."
                },
            },
        ]
        return leads

    @listen(fetch_leads)
    def score_leads(self, leads):
        lead_scoring_crew = LeadEnrichment().crew()
        scores = lead_scoring_crew.kickoff_for_each(leads)
        self.state["score_crews_results"] = scores
        return scores

    @listen(score_leads)
    def store_leads_score(self, scores):
        # Here we would store the scores in the database
        return scores

    @listen(score_leads)
    def filter_leads(self, scores):
        return [score for score in scores if score['lead_score'].score > 70]

    @listen(filter_leads)
    def write_email(self, leads):
        email_writing_crew = EmailWriting().crew();
        scored_leads = [lead.to_dict() for lead in leads]
        emails = email_writing_crew.kickoff_for_each(scored_leads)
        return emails

    @listen(write_email)
    def send_email(self, emails):
        # Here we would send the emails to the leads
        return emails

def kickoff():
    """
    Run the flow.
    """
    sales_pipeline_flow = SalesPipeline()
    result = sales_pipeline_flow.kickoff()
    # Calculate Costs
    print("**********************")
    # for idx, lead_result in enumerate(sales_pipeline_flow.state["score_crews_result"]):
    #     total_tokens = lead_result.token_usage.total_tokens
    #     cost_per_millions_tokens = 0.150
    #     total_cost = (total_tokens/1_000_000) * cost_per_millions_tokens

    #     print(f"Total Tokens Used: {total_tokens}")
    #     print(f"Estimated cost: ${total_cost:.4f}")
    print("**********************")
    return result        

def plot():
    """
    Plot the flow.
    """
    sales_pipeline = SalesPipeline()
    sales_pipeline.plot()


if __name__ == "__main__":
    kickoff()
    