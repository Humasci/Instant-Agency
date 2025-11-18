#!/usr/bin/env python3
"""
Import SIX3 Workflows into n8n Cloud Instance
Imports pre-built workflow JSON files into https://n8n.six3.cloud
"""

import json
import os
from agents.n8n_integration import n8n

def import_workflow_file(file_path: str):
    """Import a workflow JSON file into n8n"""
    try:
        print(f"📄 Importing workflow from: {file_path}")
        
        with open(file_path, 'r') as f:
            workflow_data = json.load(f)
        
        workflow_name = workflow_data.get('name', 'Unknown Workflow')
        print(f"🔧 Workflow Name: {workflow_name}")
        
        # Create the workflow in n8n
        result = n8n.create_six3_workflow(workflow_name, workflow_data)
        
        if result['success']:
            print(f"✅ Successfully imported: {workflow_name}")
            print(f"   Workflow ID: {result['workflow']['id']}")
            print(f"   Active: {result['workflow']['active']}")
            return True
        else:
            print(f"❌ Failed to import {workflow_name}: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing {file_path}: {e}")
        return False

def main():
    """Import all SIX3 workflows"""
    print("🚀 SIX3 WORKFLOW IMPORT TOOL")
    print("="*50)
    print(f"🌐 Target n8n Instance: {n8n.base_url}")
    
    # List of workflow files to import
    workflow_files = [
        "workflows/SIX3_Lead_Qualification.json",
        "workflows/SIX3_Email_Personalization.json",
        "workflows/SIX3_Search_Marketing_Campaign.json",
        "workflows/SIX3_AI_Avatar_Production.json",
        "workflows/SIX3_ML_Model_FineTuning.json",
        "workflows/SIX3_Generative_AI_Video_Production.json",
        "workflows/SIX3_Client_Onboarding.json"
    ]
    
    successful_imports = 0
    total_workflows = len(workflow_files)
    
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            success = import_workflow_file(workflow_file)
            if success:
                successful_imports += 1
        else:
            print(f"❌ File not found: {workflow_file}")
        
        print()  # Empty line for readability
    
    print(f"📊 IMPORT SUMMARY")
    print(f"   Total workflows: {total_workflows}")
    print(f"   Successfully imported: {successful_imports}")
    print(f"   Failed: {total_workflows - successful_imports}")
    
    if successful_imports > 0:
        print(f"\n🎉 Access your workflows at: {n8n.base_url}")
        
        # Show current workflows in n8n
        print(f"\n🔄 Verifying workflows in n8n...")
        workflows = n8n.get_workflows()
        print(f"✅ Found {len(workflows)} SIX3 workflows in n8n:")
        for wf in workflows:
            status = "🟢 Active" if wf.get('active') else "🔴 Inactive"
            print(f"   • {wf.get('name')} - {status}")

if __name__ == "__main__":
    main()