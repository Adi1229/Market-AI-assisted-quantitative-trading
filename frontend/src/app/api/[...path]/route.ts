import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const API_TOKEN = process.env.MARKET_API_TOKEN || "";

export async function GET(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const resolvedParams = await params;
  return proxyRequest(req, resolvedParams.path);
}

export async function POST(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const resolvedParams = await params;
  return proxyRequest(req, resolvedParams.path);
}

export async function PUT(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const resolvedParams = await params;
  return proxyRequest(req, resolvedParams.path);
}

export async function DELETE(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const resolvedParams = await params;
  return proxyRequest(req, resolvedParams.path);
}

async function proxyRequest(req: NextRequest, pathArray: string[]) {
  try {
    const path = pathArray.join("/");
    const url = new URL(`${BACKEND_URL}/${path}`);
    
    // Copy search params (query strings)
    url.search = req.nextUrl.search;

    const headers = new Headers(req.headers);
    // Inject backend API token securely
    headers.set("Authorization", `Bearer ${API_TOKEN}`);
    // Don't forward host to avoid mismatched domain issues
    headers.delete("host");

    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
    };

    if (req.method !== "GET" && req.method !== "HEAD") {
      const body = await req.text();
      fetchOptions.body = body;
    }

    const response = await fetch(url.toString(), fetchOptions);

    const responseHeaders = new Headers(response.headers);
    // Remove headers that might cause issues when proxying
    responseHeaders.delete("content-encoding");

    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error: any) {
    console.error("Proxy error:", error);
    return NextResponse.json(
      { error: "Internal Server Error from Next.js proxy" },
      { status: 500 }
    );
  }
}
