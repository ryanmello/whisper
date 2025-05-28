"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { validateGitHubUrl } from "@/lib/api";

interface RepositorySelectorProps {
  onRepoSelect: (repo: string) => void;
}

interface GitHubRepo {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  forks_count: number;
  updated_at: string;
  private: boolean;
}

interface GitHubUser {
  login: string;
  avatar_url: string;
  name: string | null;
}

export default function RepositorySelector({
  onRepoSelect,
}: RepositorySelectorProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [repositories, setRepositories] = useState<GitHubRepo[]>([]);
  const [user, setUser] = useState<GitHubUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  // For demo purposes - in production, you'd get this from OAuth callback
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [token, setToken] = useState("");
  
  // URL input functionality
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");

  // Check for stored GitHub token on component mount
  useEffect(() => {
    const storedToken = localStorage.getItem("github_token");
    if (storedToken) {
      setToken(storedToken);
      // Auto-connect with stored token
      handleTokenConnect(storedToken);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // GitHub OAuth configuration 
  const GITHUB_CLIENT_ID = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
  const REDIRECT_URI = "http://localhost:3000/auth/callback";
  const SCOPES = "repo user";

  const handleGitHubAuth = () => {
    // Check if GitHub OAuth is configured
    if (!GITHUB_CLIENT_ID || GITHUB_CLIENT_ID === process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID) {
      setError("GitHub OAuth not configured. Please set up your GitHub OAuth app and update the environment variables, or use the token fallback below.");
      setShowTokenInput(true);
      return;
    }

    // Redirect to GitHub OAuth
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(
      REDIRECT_URI
    )}&scope=${encodeURIComponent(SCOPES)}`;
    
    window.location.href = githubAuthUrl;
  };

  const handleTokenConnect = async (providedToken?: string) => {
    const activeToken = providedToken || token;
    if (!activeToken.trim()) {
      setError("Please enter a GitHub token");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // First, verify the token and get user info
      const userResponse = await fetch("https://api.github.com/user", {
        headers: {
          Authorization: `token ${activeToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!userResponse.ok) {
        throw new Error("Invalid token or API error");
      }

      const userData = await userResponse.json();
      setUser(userData);

      // Then fetch repositories
      const reposResponse = await fetch(
        "https://api.github.com/user/repos?sort=updated&per_page=50",
        {
          headers: {
            Authorization: `token ${activeToken}`,
            Accept: "application/vnd.github.v3+json",
          },
        }
      );

      if (!reposResponse.ok) {
        throw new Error("Failed to fetch repositories");
      }

      const reposData = await reposResponse.json();
      setRepositories(reposData);
      setIsConnected(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setToken("");
    setRepositories([]);
    setUser(null);
    setError(null);
    setShowTokenInput(false);
    setShowUrlInput(false);
    setRepoUrl("");
    // Clear stored token
    localStorage.removeItem("github_token");
  };

  const handleUrlSubmit = () => {
    if (!repoUrl.trim()) {
      setError("Please enter a repository URL");
      return;
    }

    if (!validateGitHubUrl(repoUrl)) {
      setError("Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)");
      return;
    }

    // Extract owner/repo from URL and pass it to onRepoSelect
    const match = repoUrl.match(/github\.com\/([^\/]+\/[^\/]+)/);
    if (match) {
      onRepoSelect(repoUrl); // Pass the full URL
    } else {
      setError("Invalid GitHub URL format");
    }
  };

  const getLanguageColor = (language: string | null) => {
    if (!language) return "bg-gray-500";

    const colors: Record<string, string> = {
      TypeScript: "bg-blue-500",
      JavaScript: "bg-yellow-500",
      Python: "bg-green-500",
      Java: "bg-red-500",
      "C++": "bg-purple-500",
      Go: "bg-cyan-500",
      Rust: "bg-orange-500",
      PHP: "bg-indigo-500",
      Ruby: "bg-red-400",
      Swift: "bg-orange-400",
    };
    return colors[language] || "bg-gray-500";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffInDays === 0) return "today";
    if (diffInDays === 1) return "yesterday";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    return `${Math.floor(diffInDays / 365)} years ago`;
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-12 h-12 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">W</span>
            </div>
            <CardTitle className="text-2xl">Welcome to Whisper</CardTitle>
            <CardDescription>
              Connect your GitHub account to get started with AI-powered code
              analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!showTokenInput && !showUrlInput ? (
              <>
                <Button
                  onClick={handleGitHubAuth}
                  className="w-full bg-black hover:bg-gray-800"
                  size="lg"
                >
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Authorize with GitHub
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">
                      Or
                    </span>
                  </div>
                </div>

                <Button
                  variant="outline"
                  onClick={() => setShowTokenInput(true)}
                  className="w-full"
                >
                  Use Personal Access Token
                </Button>

                <Button
                  variant="outline"
                  onClick={() => setShowUrlInput(true)}
                  className="w-full"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  Analyze Any Public Repository
                </Button>

                <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                  <p className="text-xs text-blue-800">
                    <strong>Setup Required:</strong> To use GitHub OAuth, you
                    need to:
                  </p>
                  <ul className="text-xs text-blue-700 mt-1 ml-4 list-disc">
                    <li>Create a GitHub OAuth App</li>
                    <li>Set your Client ID in the code</li>
                    <li>
                      Configure callback URL:{" "}
                      <code>http://localhost:3000/auth/callback</code>
                    </li>
                  </ul>
                </div>
              </>
            ) : showUrlInput ? (
              <>
                <div>
                  <label htmlFor="repo-url" className="block text-sm font-medium text-gray-700 mb-2">
                    GitHub Repository URL
                  </label>
                  <input
                    id="repo-url"
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && handleUrlSubmit()}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter any public GitHub repository URL to analyze
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowUrlInput(false)}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button
                    onClick={handleUrlSubmit}
                    disabled={!repoUrl.trim()}
                    className="flex-1 bg-black hover:bg-gray-800 disabled:opacity-50"
                  >
                    Analyze Repository
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div>
                  <label
                    htmlFor="token"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    GitHub Personal Access Token
                  </label>
                  <input
                    id="token"
                    type="password"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Need a token?{" "}
                    <a
                      href="https://github.com/settings/tokens"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Create one here
                    </a>
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowTokenInput(false)}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button
                    onClick={() => handleTokenConnect()}
                    disabled={isLoading || !token.trim()}
                    className="flex-1 bg-black hover:bg-gray-800 disabled:opacity-50"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                        Connecting...
                      </div>
                    ) : (
                      "Connect"
                    )}
                  </Button>
                </div>
              </>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">W</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Select Repository
              </h1>
              <p className="text-gray-600">
                Choose a repository to analyze and work with
              </p>
            </div>
            <div className="ml-auto flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowUrlInput(true)}
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Analyze URL
              </Button>
              <Button
                variant="outline"
                onClick={handleDisconnect}
              >
                Disconnect
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-3 mb-6">
            <Avatar className="w-8 h-8">
              <AvatarImage src={user?.avatar_url} />
              <AvatarFallback>
                {user?.login.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-sm text-gray-600">
              Connected as <strong>{user?.name || user?.login}</strong>
            </span>
            <Badge variant="secondary" className="ml-auto">
              {repositories.length} repositories
            </Badge>
          </div>
        </div>

        {/* URL Input Modal */}
        {showUrlInput && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Analyze Repository by URL</CardTitle>
                <CardDescription>
                  Enter any public GitHub repository URL to analyze
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="repo-url-modal" className="block text-sm font-medium text-gray-700 mb-2">
                    GitHub Repository URL
                  </label>
                  <input
                    id="repo-url-modal"
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && handleUrlSubmit()}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowUrlInput(false);
                      setRepoUrl("");
                      setError(null);
                    }}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleUrlSubmit}
                    disabled={!repoUrl.trim()}
                    className="flex-1 bg-black hover:bg-gray-800 disabled:opacity-50"
                  >
                    Analyze Repository
                  </Button>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {repositories.map((repo) => (
            <Card
              key={repo.id}
              className="cursor-pointer hover:shadow-lg transition-shadow duration-200 border-2 hover:border-blue-200"
              onClick={() => onRepoSelect(`https://github.com/${repo.full_name}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-lg">{repo.name}</CardTitle>
                      {repo.private && (
                        <Badge variant="secondary" className="text-xs">
                          Private
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="text-sm mb-3">
                      {repo.description || "No description provided"}
                    </CardDescription>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {repo.language && (
                    <div className="flex items-center gap-1">
                      <div
                        className={`w-3 h-3 rounded-full ${getLanguageColor(
                          repo.language
                        )}`}
                      ></div>
                      <span>{repo.language}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <svg
                      className="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span>{repo.stargazers_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg
                      className="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M7.707 3.293a1 1 0 010 1.414L5.414 7H11a7 7 0 017 7v2a1 1 0 11-2 0v-2a5 5 0 00-5-5H5.414l2.293 2.293a1 1 0 11-1.414 1.414L2.586 7.707a1 1 0 010-1.414L6.293 2.586a1 1 0 011.414 1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span>{repo.forks_count}</span>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <Separator className="mb-3" />
                <p className="text-xs text-gray-500">
                  Updated {formatDate(repo.updated_at)}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {repositories.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No repositories found
            </h3>
            <p className="text-gray-600">
              It looks like you don&apos;t have any repositories yet.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
