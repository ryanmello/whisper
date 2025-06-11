"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { WhisperAPI } from "@/lib/api";
import { Textarea } from './ui/textarea';

interface GitHubPRDialogProps {
  repository: string;
  vulnerabilityResults?: any;
  onClose: () => void;
  onSuccess: (prUrl: string) => void;
}

export function GitHubPRDialog({ 
  repository, 
  vulnerabilityResults, 
  onClose, 
  onSuccess 
}: GitHubPRDialogProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [prTitle, setPrTitle] = useState("Security: Fix dependency vulnerabilities");
  const [prDescription, setPrDescription] = useState("");
  const [targetBranch, setTargetBranch] = useState("main");
  const [dryRun, setDryRun] = useState(true);

  const handleCreatePR = async () => {
    setIsCreating(true);
    try {
      // Extract repository owner and name from URL
      const match = repository.match(/github\.com\/([^\/]+)\/([^\/]+)/);
      if (!match) {
        throw new Error("Invalid GitHub repository URL");
      }
      
      const [, owner, repo] = match;
      
      const response = await WhisperAPI.createSecurityPR({
        repository: repository,
        owner: owner,
        repo: repo.replace('.git', ''),
        title: prTitle,
        description: prDescription,
        target_branch: targetBranch,
        dry_run: dryRun,
        vulnerability_data: vulnerabilityResults
      });

      if (response.success) {
        onSuccess(response.pr_url || response.preview_url || "PR created successfully");
      } else {
        throw new Error(response.error || "Failed to create PR");
      }
    } catch (error) {
      console.error("Error creating PR:", error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsCreating(false);
    }
  };

  const vulnerabilityCount = vulnerabilityResults?.scan_summary?.vulnerabilities_found || 0;
  const riskLevel = vulnerabilityResults?.scan_summary?.risk_level || "UNKNOWN";

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>🔧 Create Security Fix PR</span>
            <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Vulnerability Summary */}
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Security Issues Found</h3>
            <div className="flex items-center gap-4">
              <Badge className={`
                ${riskLevel === 'CRITICAL' ? 'bg-red-600' :
                  riskLevel === 'HIGH' ? 'bg-orange-600' :
                  riskLevel === 'MEDIUM' ? 'bg-yellow-600' :
                  'bg-green-600'}
              `}>
                {riskLevel} RISK
              </Badge>
              <span className="text-sm text-gray-600">
                {vulnerabilityCount} vulnerabilities found
              </span>
            </div>
          </div>

          {/* PR Configuration */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">PR Title</label>
              <Input
                value={prTitle}
                onChange={(e) => setPrTitle(e.target.value)}
                placeholder="Security: Fix dependency vulnerabilities"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Target Branch</label>
              <Input
                value={targetBranch}
                onChange={(e) => setTargetBranch(e.target.value)}
                placeholder="main"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description (Optional)</label>
              <Textarea
                value={prDescription}
                onChange={(e) => setPrDescription(e.target.value)}
                placeholder="Additional details about the security fixes..."
                rows={4}
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="dryRun"
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="dryRun" className="text-sm">
                Dry run (preview changes without creating PR)
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button 
              onClick={handleCreatePR} 
              disabled={isCreating || !prTitle.trim()}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            >
              {isCreating ? (
                <>🔄 Creating...</>
              ) : (
                <>🔧 {dryRun ? 'Preview' : 'Create'} PR</>
              )}
            </Button>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-500 pt-2 border-t">
            This will analyze your go.mod file and create a pull request with updated dependencies to fix security vulnerabilities.
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 