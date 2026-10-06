# Windows preview 1.0.10

- New scan layout selector: existing categories or provider / creator / type / family.
- Proposes reorganizing existing libraries; keeps confirmed routing separately per layout.
- Verified Civitai creators and Hugging Face namespaces; unknown creator/type stays in place for review.
- Recognizes ComfyUI workflow JSON alongside supported model files.
- Existing source TXT moves with its model; missing notes can be generated without duplicate TXT.
- Removes only empty former source folders after approved creator-layout moves and records changes for restoration. Models, unrelated data, independent duplicate copies and existing hard-link aliases are preserved. Conflicts are not overwritten.

ComfyUI model-search settings may need adjustment for provider-first layouts. Source metadata availability limits creator identification. Unsigned Windows preview; no second-PC/VM validation claimed. MIT project license. No personal model data included; no GitHub push or release performed.
