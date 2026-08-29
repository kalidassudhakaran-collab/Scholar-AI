import { FeatureWorkspace } from "@/components/features/FeatureWorkspace";

export default function PlagiarismPage() {
  return (
    <FeatureWorkspace
      title="Plagiarism Checker"
      description="Compare documents for semantic similarity."
      feature="plagiarism"
      endpoint="/plagiarism/run/"
    />
  );
}
