"use client";
import { ScrollStage } from "@/components/landing/scroll-stage";
import { Hero } from "@/components/landing/hero";
import { HorizontalReel } from "@/components/landing/horizontal-reel";
import { Playground } from "@/components/landing/playground";
import { ExplodedOutro } from "@/components/landing/exploded-outro";

export default function HomePage() {
  return (
    <main className="relative">
      {
}
      <ScrollStage heroSelector="#hero" reelSelector="#reel" bufferVh={60} />
      <Hero />
      <HorizontalReel />
      <Playground />
      <ExplodedOutro />
    </main>
  );
}
