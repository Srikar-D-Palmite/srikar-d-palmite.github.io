import type { Route } from "./+types/home";
import { Welcome } from "./welcome";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Srikar Tadeparti" },
    { name: "description", content: "Welcome to my website!" },
  ];
}

export default function Home() {
  return <Welcome />;
}
