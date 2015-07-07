var gulp = require('gulp');
var sourcemaps = require('gulp-sourcemaps');
var cssmin = require('gulp-cssmin');
var bower = require('bower-files')();
var concat = require('gulp-concat');
var less = require('gulp-less');
var uglify = require('gulp-uglify');
var nodemon = require('gulp-nodemon');
var browserSync = require('browser-sync');
var reload = browserSync.reload;
var copy = require('gulp-copy');

var paths = {
  'templates': ['./mumble/templates/**/*.html'],
  'styles': ['./mumble/static/styles/**/*.less']
};

gulp.task('install_fonts', function () {
  return gulp.src('./bower_components/font-awesome/fonts/*')
    .pipe(copy('./mumble/public/fonts/', {prefix: 3}));
})

gulp.task('less', function() {
  return gulp.src(paths.styles)
    .pipe(sourcemaps.init())
    .pipe(less())
    .pipe(concat('style.css'))
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('./mumble/public/styles/'))
    .pipe(reload({stream: true}))
});

gulp.task('less_dist', function() {
  return gulp.src(paths.styles)
    .pipe(less())
    .pipe(concat('style.css'))
    .pipe(cssmin())
    .pipe(gulp.dest('./mumble/public/styles/'))
    .pipe(reload({stream: true}))
});

gulp.task('bowerdeps', function() {
  return gulp.src(bower.ext('js').files)
    .pipe(sourcemaps.init())
    .pipe(concat('libs.min.js'))
    .pipe(uglify())
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('./mumble/public/scripts/'))
});

gulp.task('bowerdeps_dist', function() {
  return gulp.src(bower.ext('js').files)
    .pipe(concat('libs.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('./mumble/public/scripts/'))
});


gulp.task('watch', ['less'], function() {

  //nodemon({
  //  exec: 'python run.py',
  //  watch: ['**/*.py']
  //})

  browserSync({
    proxy: '127.0.0.1:5002',
    files: ['public/**/*.{js,css}']
  });

  gulp.watch(paths.styles, ['less']);
  gulp.watch(paths.templates, reload)
});

gulp.task('default', ['less', 'bowerdeps']);
gulp.task('dist', ['install_fonts', 'less_dist', 'bowerdeps_dist'])
