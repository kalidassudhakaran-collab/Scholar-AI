import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";

export default function HumanizerPage() {
  return (
    <FeatureWorkspace
      title="Humanizer"
      description="Make AI-generated text sound more natural."
      feature="humanizer"
      endpoint="/humanizer/run/"
    />
  );
}
