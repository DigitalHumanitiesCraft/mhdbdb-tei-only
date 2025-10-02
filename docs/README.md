# MHDBDB Documentation Hub

**Last Updated**: 2025-10-02
**Project**: Mittelhochdeutsche Begriffsdatenbank (MHDBDB) TEI Repository

---

## 📚 Documentation Structure

This documentation is organized for **two audiences**:

### 👨‍💻 For Developers & AI Agents
Technical documentation for development, maintenance, and AI-assisted coding

### 👥 For End Users & Researchers
User-friendly guides for exploring the corpus and using the tools

---

## 🚀 Quick Start

### I'm a User - I want to explore Middle High German texts
→ **[User Guide](./USER-GUIDE.md)** - Start here!

### I'm a Developer - I want to understand the codebase
→ **[Developer Guide](./DEVELOPER-GUIDE.md)** - Technical overview

### I'm Claude Code - I need to work on this project
→ **[CLAUDE.md](../CLAUDE.md)** - Project instructions for AI agents

---

## 📖 Documentation Index

### User Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[User Guide](./USER-GUIDE.md)** | Complete guide to using MHDBDB tools | End users |
| **[Search Guide](./SEARCH-GUIDE.md)** | How to use all 11 search functions | Researchers |
| **[FAQ](./FAQ.md)** | Frequently asked questions | Everyone |
| **[Glossary](./GLOSSARY.md)** | MHG terminology & concepts | Researchers |

### Developer Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[Developer Guide](./DEVELOPER-GUIDE.md)** | Architecture, setup, development | Developers |
| **[API Reference](./API-REFERENCE.md)** | JavaScript API documentation | Developers |
| **[Testing Guide](./TESTING-GUIDE.md)** | Running and writing tests | Developers |
| **[Deployment Guide](./DEPLOYMENT-GUIDE.md)** | Production deployment steps | DevOps |

### Technical Specifications & Project Status

| Document | Description | Status |
|----------|-------------|--------|
| **[CLAUDE.md](../CLAUDE.md)** | Complete architecture & developer reference | ✅ Active |
| **[REFACTORING-SUMMARY.md](../REFACTORING-SUMMARY.md)** | Phase 7 modular UI refactoring | ✅ Active |
| **[REFACTORING-PLAN.md](../REFACTORING-PLAN.md)** | Multi-phase refactoring plan | ✅ Active |
| **[BUGFIX-2025-10-02.md](../BUGFIX-2025-10-02.md)** | Recent bug fixes & test suite improvements | ✅ Active |

---

## 🎯 Documentation Standards

All documentation in this project follows these standards:

### ✅ Structure
- Clear headings and table of contents
- Code examples with syntax highlighting
- Screenshots where helpful
- Cross-references between docs

### ✅ Style
- **User docs**: Friendly, tutorial-style, no jargon
- **Developer docs**: Technical, precise, with code samples
- **AI agent docs**: Structured, detailed, machine-readable

### ✅ Maintenance
- Last updated dates on all documents
- Version numbers where applicable
- Links verified regularly
- Outdated docs archived, not deleted

---

## 📝 Document Lifecycle

### Active Documents ✅
Currently maintained, up-to-date (October 2025)

- **[CLAUDE.md](../CLAUDE.md)** - Primary developer reference
- **[REFACTORING-SUMMARY.md](../REFACTORING-SUMMARY.md)** - Phase 7 completion
- **[BUGFIX-2025-10-02.md](../BUGFIX-2025-10-02.md)** - Recent fixes
- All docs/ files (user guides, developer docs)

### Reference Documents 📚
Historical reference, completed work

- **[REFACTORING-PLAN.md](../REFACTORING-PLAN.md)** - Multi-phase refactoring plan

### Removed Documents 🗑️
Cleaned up during Phase 7 merge (October 2, 2025)

- JS-ARCHITECTURE.md (merged into CLAUDE.md)
- TEI-PERFORMANCE-OPTIMIZATION.md (obsolete, architecture changed)
- BROWSER-COMPATIBILITY.md (obsolete)
- REWORK-STATUS.md (obsolete, work completed)
- PHASE-3-COMPLETION.md (obsolete)
- CODEBASE-STATUS-REPORT.md (obsolete)
- REWORK.md (obsolete, 3325 lines removed)

---

## 🔍 Finding What You Need

### "How do I use the search functions?"
→ [Search Guide](./SEARCH-GUIDE.md)

### "How does the caching work?"
→ [Developer Guide](./DEVELOPER-GUIDE.md#caching-strategy)

### "What's the 3-stage lemma resolution?"
→ [CLAUDE.md](../CLAUDE.md#multi-lemma-variant-resolution)

### "How do I run tests?"
→ [Testing Guide](./TESTING-GUIDE.md)

### "Where are the API docs?"
→ [API Reference](./API-REFERENCE.md)

### "How do I deploy this?"
→ [Deployment Guide](./DEPLOYMENT-GUIDE.md)

---

## 🤝 Contributing to Documentation

### Adding New Documentation

1. Choose the correct directory:
   - `docs/` - All new documentation
   - Root - Only project instructions (CLAUDE.md, README.md)

2. Follow naming conventions:
   - User docs: `*-GUIDE.md` (e.g., SEARCH-GUIDE.md)
   - Technical: `*-REFERENCE.md` (e.g., API-REFERENCE.md)
   - AI agent: `CLAUDE.md` or `*-STATUS.md`

3. Update this index (docs/README.md)

4. Add cross-references from existing docs

### Documentation Checklist

When creating/updating docs:

- [ ] Add "Last Updated" date at top
- [ ] Include table of contents for long docs
- [ ] Add code examples with syntax highlighting
- [ ] Link to related documentation
- [ ] Update this index
- [ ] Test all links
- [ ] Get review (if major changes)

---

## 📊 Documentation Statistics

**As of October 2, 2025:**

```
Root Documentation:   5 active files
- CLAUDE.md                    (primary developer reference)
- README.md                    (user-facing overview)
- REFACTORING-SUMMARY.md       (Phase 7 completion)
- REFACTORING-PLAN.md          (refactoring roadmap)
- BUGFIX-2025-10-02.md         (recent fixes)

User Documentation:   6 files in docs/
- README.md, USER-GUIDE.md, SEARCH-GUIDE.md
- FAQ.md, GLOSSARY.md, DEVELOPER-GUIDE.md

Removed Documents:    7 obsolete files (5,536 lines cleaned up)
```

---

## 🔗 External Resources

- **MHDBDB Official Site**: https://mhdbdb.plus.ac.at
- **TEI Guidelines**: https://tei-c.org/guidelines/
- **Project Repository**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only
- **Issue Tracker**: https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues

---

## 📧 Contact & Support

For questions about:

- **Using the tools**: See [User Guide](./USER-GUIDE.md) or [FAQ](./FAQ.md)
- **Development**: See [Developer Guide](./DEVELOPER-GUIDE.md)
- **Research queries**: mhdbdb@plus.ac.at
- **Technical issues**: GitHub Issues

---

**Navigation**: [↑ Back to Top](#mhdbdb-documentation-hub) | [→ User Guide](./USER-GUIDE.md) | [→ Developer Guide](./DEVELOPER-GUIDE.md)
