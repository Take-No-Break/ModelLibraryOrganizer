# Model inspection tools

1. Scan a folder in Model inspection / Preview. Select models using Ctrl / Shift.
2. Previous / Next image browses the first 50 associated public general-audience image records plus version previews.
3. Models used in this image compares image metadata with scanned local files. Find models used in image reads PNG metadata from Automatic1111 or a ComfyUI API prompt graph.
4. Check model updates lists newer public Civitai versions by publication date; review the family before downloading. No automatic replacement occurs.
5. Copy trigger words combines source words, removes duplicates and copies them. Offline uses cached words.
6. Authors lists scanned, still-existing local files grouped by author/model/version. Double-click a file to inspect it.
7. Compare version descriptions shows description and trigger-word line differences: additions green, removals red.

API access and absent metadata can limit results. Hash/version matches are distinct from unverified filename matches. Not identified does not prove a model is absent from the PC. No models are inferred from pixels. Author lists cover local models only. Version comparisons cover public text, not model weights or compatibility.

## Labels and image metadata

- **Model type** describes a role: checkpoint, LoRA, embedding, VAE, and so on.
- **Base model family** describes the source base model or lineage, such as Illustrious, Pony or Anima. It is not a tag and does not guarantee loader compatibility.
- **Identification confidence** records the basis of identification (verified source hash, reviewed rule, structural inference or unknown); it is not a numeric probability. **Evidence** gives supporting details.
- **Find models used in image** requires supported generation metadata in a PNG: model names/hashes or a ComfyUI prompt graph. Any source can supply such a PNG; an ordinary PNG without this metadata cannot identify models from appearance. Matching can be incomplete.
