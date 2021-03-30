set mouse=v

set bg=light
set background=dark

set nopaste
set paste

set ruler

set hidden

set hlsearch
set nohlsearch

set noincsearch
set incsearch

set tabstop=8

set softtabstop=8
set shiftwidth=8

set softtabstop=4
set shiftwidth=4
set expandtab

set encoding=utf-8
" set cindent
" set autoindent
" set textwidth=80
" set smartindent
syntax off
syntax on

" set winwidth=80
" set ignorecase
set nowrap
set wrap
" set autowrite

" imap { {<CR>}<ESC>O

map <C-J> :previous<CR>
map <C-K> :next<CR>

map <C-N> :bprevious<CR>
" map <C-M> :bnext<CR>

map <F1> :call VComment()<CR>
map <F2> :set number!<CR>
map <F3> :call CComment2()<CR>
map <F4> :call SComment()<CR>
map <F5> :call RemovePlus()<CR>
map <F6> :call Endif()<CR>

map <F7> :retab!<CR>
" map <F7> :!make<CR>:!make run<CR>
" imap <F7> <ESC>:!make<CR>:!make run<CR>
map <F8> :!make -j 32<CR>
imap <F8> <ESC>:w<ESC>:!make all<CR>
map <F9> :w<CR>:!make run<CR>

map <F10> :!make clean<CR>
" map <F11> :!make clean<CR>:!make<CR>:!make run<CR>
map <F12> :set hlsearch!<CR>

map <c-w><c-o> <c-w><c-p>
map <c-w>o <c-w><c-p>

function Syn()
	:color default
	:set bg=dark
endfunc

function CComment()
	let line = getline(".")
	if line[0][0] == "/"
		:s/\/\/ //
	else
		:s/^/\/\/ /
	endif
endfunc

function CComment2()
	let line = getline(".")
	if line[0][0] == "/"
		:s/\/\* //
		:s/ \*\///
	else
		:s/^/\/\* /
		:s/$/ \*\//
	endif
endfunc

function SComment()
	let line = getline(".")
	if line[0][0] == "#"
		:s/^# //
	else
		:s/^/# /
	endif
endfunc

function VComment()
	let line = getline(".")
	if line[0][0] == "\""
		:s/^" //
	else
		:s/^/" /
	endif
endfunc

function RemovePlus()
	let line = getline(".")
	if line[0][0] == "\+"
		:%s/^+//
	endif
endfunc

function Endif()
	s/$/\r#endif/
endfunc

function OVS()
	set softtabstop=4
	set shiftwidth=4
	set expandtab
endfunc

function Linux()
	set softtabstop=8
	set shiftwidth=8
	set noexpandtab
endfunc

" colorscheme darkZ
" colorscheme dark-ruby
" colorscheme c

set vb t_vb=     " no visual bell & flas

set laststatus=2

if &diff
	colorscheme evening
endif

" highlight Normal term=none cterm=none ctermfg=White ctermbg=Black gui=none guifg=White guibg=Black
" highlight DiffAdd cterm=none ctermfg=fg ctermbg=Blue gui=none guifg=fg guibg=Blue
" highlight DiffDelete cterm=none ctermfg=fg ctermbg=Blue gui=none guifg=fg guibg=Blue
" highlight DiffChange cterm=none ctermfg=fg ctermbg=Blue gui=none guifg=fg guibg=Blue
" highlight DiffText cterm=none ctermfg=bg ctermbg=White gui=none guifg=bg guibg=White

" set noswapfile

set term=screen

" set csprg=/usr/bin/cscope

" cs add cscope.out

" For debian, add the following lines in /etc/vim/vimrc
" if has("cscope") && filereadable("/usr/bin/cscope")
"    set csprg=/usr/bin/cscope
"    set csto=0
"    set cst
"    set nocsverb
"    if filereadable("cscope.out")
"       cs add $PWD/cscope.out
"    elseif $CSCOPE_DB != ""
"       cs add $CSCOPE_DB
"    endif
"    set csverb
" endif

" color desert
