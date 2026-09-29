(() => {
 'use strict';
 const normalize=v=>v.normalize('NFKD').toLocaleLowerCase().replace(/[’']/g,'').trim();
 const safeId=()=>{try{return decodeURIComponent(location.hash.slice(1));}catch{return '';}};
 document.querySelectorAll('[data-library]').forEach(library=>{
  const search=library.querySelector('#library-search'),items=[...library.querySelectorAll('[data-library-item]')];
  if(!search)return;
  const controls=library.querySelector('[data-filter-controls]'),status=library.querySelector('#library-results'),empty=library.querySelector('[data-library-empty]');
  controls.hidden=false;
  const filter=()=>{const words=normalize(search.value).split(/\s+/).filter(Boolean);let count=0;
   items.forEach(item=>{const match=words.every(w=>normalize(item.dataset.search||item.textContent).includes(w));item.hidden=!match;if(match)count++;else{item.querySelectorAll('iframe').forEach(p=>p.remove());const play=item.querySelector('[data-video-id]'),close=item.querySelector('.g-close');if(play)play.hidden=false;if(close)close.hidden=true;}});
   status.textContent=`${count} ${library.dataset.itemName||'items'}`;empty.hidden=count>0;
  };
  const reveal=()=>{const target=document.getElementById(safeId());const item=target?.closest('[data-library-item]');if(!item)return;search.value='';filter();target.closest('details')?.setAttribute('open','');requestAnimationFrame(()=>target.scrollIntoView({block:'center'}));};
  search.addEventListener('input',filter);library.querySelector('[data-clear-search]').addEventListener('click',()=>{search.value='';filter();search.focus();});window.addEventListener('hashchange',reveal);filter();reveal();
 });
 const grid=document.getElementById('quote-grid');
 if(grid){
  const quotes=[...grid.querySelectorAll('[data-quote]')],search=document.getElementById('quote-search'),more=document.getElementById('show-more'),status=document.getElementById('result-count'),copyStatus=document.getElementById('copy-status');
  const initial=9;let expanded=/^quote-\d+$/.test(safeId());document.querySelector('[data-quote-controls]').hidden=false;
  quotes.forEach(q=>q.querySelector('[data-quote-actions]').hidden=false);
  const render=()=>{let matches=0,shown=0;const query=normalize(search.value);quotes.forEach(q=>{const match=normalize(q.querySelector('.q-text').textContent).includes(query);const visible=match&&(query||expanded||matches<initial);if(match)matches++;q.hidden=!visible;if(visible)shown++;});more.hidden=Boolean(query)||expanded||quotes.length<=initial;more.textContent=`Show ${quotes.length-initial} more quotes`;status.textContent=query?`${shown} matching ${shown===1?'quote':'quotes'}`:`Showing ${shown} of ${quotes.length}`;};
  const reveal=()=>{if(!/^quote-\d+$/.test(safeId()))return;const q=document.getElementById(safeId());if(!q?.matches('[data-quote]'))return;expanded=true;search.value='';render();requestAnimationFrame(()=>q.scrollIntoView({block:'center'}));};
  search.addEventListener('input',render);document.getElementById('clear-search').addEventListener('click',()=>{search.value='';render();search.focus();});
  more.addEventListener('click',()=>{expanded=true;render();quotes[initial]?.focus({preventScroll:false});});
  const copy=async value=>{if(navigator.clipboard&&isSecureContext){await navigator.clipboard.writeText(value);return;}const field=document.createElement('textarea');field.value=value;field.setAttribute('readonly','');field.style.cssText='position:fixed;opacity:0';document.body.append(field);field.select();const ok=document.execCommand('copy');field.remove();if(!ok)throw new Error('clipboard unavailable');};
  grid.addEventListener('click',async e=>{const button=e.target.closest('[data-copy-quote],[data-copy-link]');if(!button)return;const quote=button.closest('[data-quote]');const address=new URL(location.pathname,location.origin);address.hash=quote.id;const value=button.hasAttribute('data-copy-quote')?quote.querySelector('.q-text').textContent:address.href;
   try{await copy(value);copyStatus.textContent=button.hasAttribute('data-copy-quote')?'Quote copied.':'Quote link copied.';}catch{copyStatus.textContent='Copy is unavailable in this browser. Select the quote or copy the page address instead.';}finally{button.focus({preventScroll:true});}
  });window.addEventListener('hashchange',reveal);render();reveal();
 }
 // Continue an explicitly chosen reading bookmark only. No storage before opt-in; no network transmission.
 if(/^\/journal\/[a-z0-9-]+\.html$/.test(location.pathname)){
  const key='ghostheart.reading.place.v1';let timeout;
  const saveProgress=()=>{try{const old=JSON.parse(localStorage.getItem(key));if(old?.path===location.pathname)localStorage.setItem(key,JSON.stringify({path:location.pathname,y:Math.max(0,Math.round(scrollY))}));}catch{}};
  addEventListener('scroll',()=>{clearTimeout(timeout);timeout=setTimeout(saveProgress,160);},{passive:true});addEventListener('pagehide',saveProgress);
 }
})();
