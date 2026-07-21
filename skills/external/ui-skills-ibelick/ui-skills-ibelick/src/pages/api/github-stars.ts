import type { APIRoute } from "astro";
import { getGithubStars } from "../../lib/github-stars.ts";

export const GET: APIRoute = async () => {
  const stars = await getGithubStars();
  return Response.json(stars, {
    headers: {
      "Cache-Control": "public, max-age=0, s-maxage=86400, must-revalidate",
    },
  });
};
