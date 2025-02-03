from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Set, Tuple

class LeadPersonalInfo(BaseModel):
    name: str = Field(..., description="The full name of the lead.")
    job_title: str = Field(..., description="The job title of the lead.")
    role_relevance: int = Field(..., ge=0, le=10, description="A score representing how relevant the lead's role is to the decision-making process (0-10).")
    professional_background: Optional[str] = Field(..., description="A brief description of the lead's professional background.")

class CompanyInfo(BaseModel):
    company_name: str = Field(..., description="The name of the company the lead works for.")
    industry: str = Field(..., description="The industry in which the company operates.")
    company_size: int = Field(..., description="The size of the company in terms of employee count.")
    revenue: Optional[float] = Field(None, description="The annual revenue of the company, if available.")
    market_presence: int = Field(..., ge=0, le=10, description="A score representing the company's market presence (0-10).")

class LeadScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="The final score assigned to the lead (0-100).")
    scoring_criteria: List[str] = Field(..., description="The criteria used to determine the lead's score.")
    validation_notes: Optional[str] = Field(None, description="Any notes regarding the validation of the lead score.")

class LeadScoringResult(BaseModel):
    personal_info: LeadPersonalInfo = Field(..., description="Personal information about the lead.")
    company_info: CompanyInfo = Field(..., description="Information about the lead's company.")
    lead_score: LeadScore = Field(..., description="The calculated score and related information for the lead.")

@CrewBase
class LeadEnrichment():
	"""LeadEnrichment crew"""
 
	agents_config = 'config/lead_qualification_agents.yaml'
	tasks_config = 'config/lead_qualification_tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def lead_data_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_data_agent'],
   			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True
 		)

	@agent
	def cultural_fit_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['cultural_fit_agent'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True
		)
	
	@agent
	def scoring_validation_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['scoring_validation_agent'],
   			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			verbose=True
		)
 
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def lead_data_task(self) -> Task:
		lead_data_agent1 = self.lead_data_agent()
		return Task(
			config=self.tasks_config['lead_data_collection'],
			agent=lead_data_agent1,
		)

	@task
	def cultural_fit_task(self) -> Task:
		cultural_fit_agent1 = self.cultural_fit_agent()
		return Task(
			config=self.tasks_config['cultural_fit_analysis'],
			agent=cultural_fit_agent1,
		)
    
	@task
	def scoring_validation_task(self) -> Task:
		scoring_validation_agent1 = self.scoring_validation_agent()
		lead_data_task1 = self.lead_data_task()
		cultural_fit_task1 = self.cultural_fit_task()
		return Task(
			config=self.tasks_config['lead_scoring_and_validation'],
			agent=scoring_validation_agent1,
			context=[lead_data_task1, cultural_fit_task1],
			output_pydantic=LeadScoringResult
		)
  
	
	@crew
	def crew(self) -> Crew:
		"""Creates the LeadEnrichment crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

	