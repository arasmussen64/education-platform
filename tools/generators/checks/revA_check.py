import glob, yaml, re, sys
tops=sorted(glob.glob('content/topics/ml.nn.*'))+['content/topics/ml.m8.checkpoint']
for t in tops:
    for f in sorted(glob.glob(t+'/recall/*.yaml')):
        d=yaml.safe_load(open(f,encoding='utf8'))
        if d.get('type')=='mcq':
            ls=[len(c) for c in d['choices']]
            a=d['answer']
            longest = ls[a]==max(ls)
            print(('LONGEST ' if longest else '        ')+f.replace(chr(92),'/').split('topics/')[1], ls, 'ans',a)
    # doubled apostrophes in block scalars
    for f in glob.glob(t+'/**/*.yaml',recursive=True)+glob.glob(t+'/*.yaml'):
        lines=open(f,encoding='utf8').read().split('\n')
        inblock=False;ind=0
        for i,l in enumerate(lines):
            m=re.match(r'^(\s*)(- )?[\w]+: [|>]-?\s*$',l) or re.match(r'^(\s*)- [|>]-?\s*$',l)
            if m: inblock=True; ind=len(m.group(1)); continue
            if inblock and l.strip() and (len(l)-len(l.lstrip()))<=ind: inblock=False
            if inblock and "''" in l: print('DOUBLE-APOS',f,i+1,l.strip()[:80])
            if l.count('`')%2: print('ODD-BACKTICK',f,i+1,l.strip()[:100])
