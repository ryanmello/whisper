"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { extractRepoName } from "@/lib/api";

interface TaskSelectorProps {
  repository: string;
  onTaskSelect: (task: string) => void;
  onStartTask: () => void;
  selectedTask: string | null;
  onBack: () => void;
}

// Mock tasks data
const suggestedTasks = [
  {
    id: "explore-codebase",
    title: "Explore Codebase",
    description: "Get a comprehensive overview of the repository structure, main components, and architecture patterns",
    icon: "🔍",
    difficulty: "Easy",
    estimatedTime: "5-10 min",
    category: "Analysis",
  },
  {
    id: "find-bugs",
    title: "Find Potential Bugs",
    description: "Scan the codebase for common programming errors, edge cases, and potential runtime issues",
    icon: "🐛",
    difficulty: "Medium",
    estimatedTime: "10-15 min",
    category: "Quality",
  },
  {
    id: "security-audit",
    title: "Security Audit",
    description: "Review code for security vulnerabilities, exposed secrets, and unsafe practices",
    icon: "🔒",
    difficulty: "Hard",
    estimatedTime: "15-20 min",
    category: "Security",
  },
  {
    id: "performance-review",
    title: "Performance Review",
    description: "Identify performance bottlenecks, memory leaks, and optimization opportunities",
    icon: "⚡",
    difficulty: "Medium",
    estimatedTime: "10-15 min",
    category: "Performance",
  },
  {
    id: "documentation-check",
    title: "Documentation Review",
    description: "Analyze code documentation completeness and suggest improvements",
    icon: "📚",
    difficulty: "Easy",
    estimatedTime: "5-10 min",
    category: "Documentation",
  },
  {
    id: "test-coverage",
    title: "Test Coverage Analysis",
    description: "Review existing tests and identify areas that need better test coverage",
    icon: "🧪",
    difficulty: "Medium",
    estimatedTime: "10-15 min",
    category: "Testing",
  },
  {
    id: "code-style",
    title: "Code Style Review",
    description: "Check code formatting, naming conventions, and style consistency",
    icon: "🎨",
    difficulty: "Easy",
    estimatedTime: "5-8 min",
    category: "Style",
  },
  {
    id: "dependency-audit",
    title: "Dependency Audit",
    description: "Review project dependencies for security issues and outdated packages",
    icon: "📦",
    difficulty: "Medium",
    estimatedTime: "8-12 min",
    category: "Dependencies",
  },
];

export default function TaskSelector({ 
  repository, 
  onTaskSelect, 
  onStartTask, 
  selectedTask, 
  onBack 
}: TaskSelectorProps) {
  
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Easy": return "bg-green-100 text-green-800";
      case "Medium": return "bg-yellow-100 text-yellow-800";
      case "Hard": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      Analysis: "bg-blue-100 text-blue-800",
      Quality: "bg-purple-100 text-purple-800",
      Security: "bg-red-100 text-red-800",
      Performance: "bg-orange-100 text-orange-800",
      Documentation: "bg-indigo-100 text-indigo-800",
      Testing: "bg-green-100 text-green-800",
      Style: "bg-pink-100 text-pink-800",
      Dependencies: "bg-cyan-100 text-cyan-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-6">
            <Button 
              variant="ghost" 
              onClick={onBack}
              className="p-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">W</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Choose a Task</h1>
              <p className="text-gray-600">
                Select a task to perform on <strong>{extractRepoName(repository)}</strong>
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {suggestedTasks.map((task) => (
            <Card 
              key={task.id}
              className={`cursor-pointer transition-all duration-200 border-2 ${
                selectedTask === task.id 
                  ? 'border-blue-500 ring-2 ring-blue-200 shadow-lg' 
                  : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
              }`}
              onClick={() => onTaskSelect(task.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div className="text-2xl">{task.icon}</div>
                  <div className="flex gap-2">
                    <Badge className={getDifficultyColor(task.difficulty)} variant="secondary">
                      {task.difficulty}
                    </Badge>
                  </div>
                </div>
                <CardTitle className="text-lg">{task.title}</CardTitle>
                <CardDescription className="text-sm">
                  {task.description}
                </CardDescription>
              </CardHeader>
              
              <CardContent>
                <Separator className="mb-3" />
                <div className="flex items-center justify-between text-sm">
                  <Badge className={getCategoryColor(task.category)} variant="outline">
                    {task.category}
                  </Badge>
                  <span className="text-gray-500">{task.estimatedTime}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {selectedTask && (
          <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2">
            <Card className="bg-white shadow-lg border-2 border-blue-200">
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className="text-lg">
                    {suggestedTasks.find(t => t.id === selectedTask)?.icon}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">
                      {suggestedTasks.find(t => t.id === selectedTask)?.title}
                    </p>
                    <p className="text-sm text-gray-600">
                      Ready to start this task on {extractRepoName(repository)}
                    </p>
                  </div>
                  <Button 
                    onClick={onStartTask}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Start Task
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
} 