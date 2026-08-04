import Hero from "@/components/home/Hero";
import CategoryCards from "@/components/home/CategoryCards";
import ComparisonCards from "@/components/home/ComparisonCards";
import AuthorityStats from "@/components/home/AuthorityStats";
import { Reveal } from "@/components/ui/reveal";

export default function Home() {
  return (
    <div className="mx-auto max-w-[1200px] px-6">
      <Hero />
      <Reveal>
        <CategoryCards />
      </Reveal>
      <Reveal>
        <ComparisonCards />
      </Reveal>
      <Reveal>
        <AuthorityStats />
      </Reveal>
    </div>
  );
}
