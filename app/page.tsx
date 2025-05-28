"use client";

import RepositorySelector from "@/components/RepositorySelector";
import TaskExecution from "@/components/TaskExecution";
import TaskSelector from "@/components/TaskSelector";
import { useState } from "react";

export default function Home() {
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [isTaskStarted, setIsTaskStarted] = useState(false);

  const handleRepoSelect = (repo: string) => {
    setSelectedRepo(repo);
  };

  const handleTaskSelect = (task: string) => {
    setSelectedTask(task);
  };

  const handleStartTask = () => {
    setIsTaskStarted(true);
  };

  const handleBackToRepo = () => {
    setSelectedRepo(null);
    setSelectedTask(null);
    setIsTaskStarted(false);
  };

  const handleBackToTasks = () => {
    setSelectedTask(null);
    setIsTaskStarted(false);
  };

  if (isTaskStarted && selectedRepo && selectedTask) {
    return (
      <TaskExecution
        repository={selectedRepo}
        task={selectedTask}
        onBack={handleBackToTasks}
      />
    );
  }

  if (selectedRepo) {
    return (
      <TaskSelector
        repository={selectedRepo}
        onTaskSelect={handleTaskSelect}
        onStartTask={handleStartTask}
        selectedTask={selectedTask}
        onBack={handleBackToRepo}
      />
    );
  }

  return <RepositorySelector onRepoSelect={handleRepoSelect} />;
}
