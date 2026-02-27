# Frontend UI Modernization - Execution Plan

## Summary

Transform the frontend from a basic light-only theme to a modern design with:
- Deep blue/purple gradient color scheme
- Glass morphism effects (backdrop blur, transparency, soft shadows)
- Automatic dark/light mode via `prefers-color-scheme`

## Pre-Flight Status

- **Backend**: Known test failure in `test_annotation_replacer.py` (expected per CLAUDE.md)
- **Frontend**: Build succeeds cleanly

## Implementation Tasks

16 tasks organized in 4 phases, following the detailed plan at `.agents/plans/frontend-ui-modernization.md`:

### Phase 1: Foundation

1. **Task 1**: Update `frontend/tailwind.config.js`
   - Add `darkMode: 'media'`
   - Add custom shadow utilities (`shadow-glass`, `shadow-glow`)
   - Keep existing primary colors, add `950` shade

2. **Task 2**: Update `frontend/src/index.css`
   - Add `@layer base` with dark mode body styles
   - Add `@layer utilities` with `bg-mesh-gradient` and `bg-mesh-gradient-light`

### Phase 2: Layout Components

3. **Task 3**: Update `frontend/src/components/layout/Layout.tsx`
   - Replace `bg-gray-50` with gradient background classes

4. **Task 4**: Update `frontend/src/components/layout/Header.tsx`
   - Convert to glass morphism (`backdrop-blur-xl`, transparency)
   - Add gradient icon background

5. **Task 5**: Update `frontend/src/components/layout/Footer.tsx`
   - Add glass morphism and dark mode support

### Phase 3: Core UI Components

6. **Task 6**: Update `frontend/src/components/ui/Card.tsx`
   - Add glass morphism effect and dark mode variants

7. **Task 7**: Update `frontend/src/components/ui/Button.tsx`
   - Add gradient primary variant
   - Add dark mode support for all variants

8. **Task 8**: Update `frontend/src/components/ui/Alert.tsx`
   - Add dark mode variants for all alert types

9. **Task 9**: Update `frontend/src/components/ui/Spinner.tsx`
   - Update to purple color with dark mode variant

### Phase 4: Feature Components

10. **Task 10**: Update `frontend/src/features/upload/components/DropZone.tsx`
    - Add glass effect and dark mode for all states

11. **Task 11**: Update `frontend/src/features/upload/components/FileInfo.tsx`
    - Add dark mode support to success card

12. **Task 12**: Update `frontend/src/features/convert/components/ConversionPanel.tsx`
    - Add dark mode to text and background colors

13. **Task 13**: Update `frontend/src/features/convert/components/DirectionSelector.tsx`
    - Add dark mode for radio buttons and labels

14. **Task 14**: Update `frontend/src/features/convert/components/ProgressDisplay.tsx`
    - Update step indicator colors for dark mode

15. **Task 15**: Update `frontend/src/features/download/components/DownloadButton.tsx`
    - Add gradient styling matching new button design

16. **Task 16**: Update `frontend/src/App.tsx`
    - Update text colors with dark mode variants

## Critical Files

| File | Action |
|------|--------|
| `frontend/tailwind.config.js` | Add darkMode, shadows |
| `frontend/src/index.css` | Add gradients, base styles |
| `frontend/src/components/layout/*.tsx` | Glass morphism |
| `frontend/src/components/ui/*.tsx` | Dark mode variants |
| `frontend/src/features/**/*.tsx` | Dark mode + glass |

## Validation Commands

```bash
# After each task:
cd frontend && npm run build

# Type checking:
cd frontend && npx tsc --noEmit

# Visual testing:
cd frontend && npm run dev
# Then toggle system dark mode in browser DevTools
```

## Verification Checklist

- [ ] `npm run build` succeeds
- [ ] `npx tsc --noEmit` passes
- [ ] Light mode: subtle gradient visible, glass cards work
- [ ] Dark mode: rich gradient visible, proper contrast
- [ ] All interactive states work (hover, focus, disabled)
- [ ] Full upload → convert → download flow works in both modes

## Notes

- Using `darkMode: 'media'` for automatic system detection (no toggle needed)
- Glass morphism uses `backdrop-blur-xl` + transparency
- Gradient buttons: `from-blue-600 to-purple-600`
- All dark mode classes use `dark:` prefix pattern
